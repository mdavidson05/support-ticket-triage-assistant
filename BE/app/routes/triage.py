from http.client import HTTPException
from fastapi import APIRouter
from pydantic import BaseModel
from app.models.ticket import TicketTriage
from app.services.triage_service import triage_ticket_with_llm

router = APIRouter(prefix="/api", tags=["triage"])


class TriageRequest(BaseModel):
    ticket_text: str


@router.post("/triage", response_model=TicketTriage)
def triage_ticket(request: TriageRequest):
    try:
        return triage_ticket_with_llm(request.ticket_text)
    except Exception as e:
        raise HTTPException(500, str(e))