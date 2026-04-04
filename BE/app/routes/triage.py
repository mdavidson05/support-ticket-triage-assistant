from fastapi import APIRouter
from pydantic import BaseModel
from app.models.ticket import TicketTriage

router = APIRouter(prefix="/api", tags=["triage"])


class TriageRequest(BaseModel):
    ticket_text: str


@router.post("/triage", response_model=TicketTriage)
def triage_ticket(request: TriageRequest):
    return TicketTriage(
        category="authentication",
        urgency="high",
        suggested_team="account_access",
        sentiment="frustrated",
        summary="Customer cannot log in after password reset.",
        recommended_next_action="Investigate account access issue and verify password reset flow."
    )