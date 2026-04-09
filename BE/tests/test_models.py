import pytest
from pydantic import ValidationError
from app.models.ticket import TicketTriage


VALID = {
    "category": "billing",
    "urgency": "medium",
    "suggested_team": "billing_ops",
    "sentiment": "neutral",
    "summary": "Customer was charged twice.",
    "recommended_next_action": "Issue a refund.",
}


def test_valid_triage_instantiates():
    triage = TicketTriage(**VALID)
    assert triage.category == "billing"
    assert triage.warnings == []


def test_warnings_defaults_to_empty_list():
    triage = TicketTriage(**VALID)
    assert triage.warnings == []


def test_invalid_category_raises():
    with pytest.raises(ValidationError):
        TicketTriage(**{**VALID, "category": "nonsense"})


def test_invalid_urgency_raises():
    with pytest.raises(ValidationError):
        TicketTriage(**{**VALID, "urgency": "urgent"})


def test_invalid_suggested_team_raises():
    with pytest.raises(ValidationError):
        TicketTriage(**{**VALID, "suggested_team": "unknown_team"})


def test_invalid_sentiment_raises():
    with pytest.raises(ValidationError):
        TicketTriage(**{**VALID, "sentiment": "happy"})