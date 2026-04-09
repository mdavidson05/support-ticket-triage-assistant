import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.ticket import TicketTriage

client = TestClient(app)

MOCK_TRIAGE = TicketTriage(
    category="billing",
    urgency="medium",
    suggested_team="billing_ops",
    sentiment="neutral",
    summary="Customer was charged twice for the same subscription.",
    recommended_next_action="Verify duplicate charge and issue refund.",
)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_triage_returns_result():
    with patch("app.routes.triage.triage_ticket_with_llm", return_value=MOCK_TRIAGE):
        response = client.post("/api/triage", json={"ticket_text": "I was charged twice."})
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "billing"
    assert data["urgency"] == "medium"
    assert data["suggested_team"] == "billing_ops"


def test_triage_missing_body_returns_422():
    response = client.post("/api/triage", json={})
    assert response.status_code == 422


def test_triage_service_error_returns_500():
    with patch("app.routes.triage.triage_ticket_with_llm", side_effect=Exception("API down")):
        response = client.post("/api/triage", json={"ticket_text": "I was charged twice."})
    assert response.status_code == 500