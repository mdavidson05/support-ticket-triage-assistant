from app.models.ticket import TicketTriage

def generate_warnings(ticket_text:str, triage: TicketTriage) -> list[str]:
    warnings = []

    if len(ticket_text.strip()) < 15:
        warnings.append("Ticket text is too short to triage reliably")
    
    if len(triage.summary) < 15:
        warnings.append("Summary is unusually short - triage may be incomplete")
    
    if triage.category == "other":
        warnings.append("Category could not be determined - manual review required")
    
    if triage.urgency == "critical" :
        warnings.append("Critical urgency flagged - review this immediately")
    
    return warnings