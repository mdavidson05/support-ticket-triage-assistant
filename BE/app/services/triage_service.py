import anthropic
from app.services.warnings import generate_warnings
from app.prompts.triage_prompt import TRIAGE_PROMPT_TEMPLATE
from app.services.llm_client import client
from app.models.ticket import TicketTriage
from fastapi import HTTPException

def triage_ticket_with_llm(ticket_text: str) -> TicketTriage:
    try:
        response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        temperature = 0,
        system=TRIAGE_PROMPT_TEMPLATE,
        tools=[{
            "name": "triage_ticket",
            "description": "Triage a support ticket",
            "input_schema": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["authentication", "billing", "bug", "feature_request", "account_management", "integration", "performance", "other"]},
                    "urgency": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "suggested_team": {"type": "string", "enum": ["account_access", "billing_ops", "support_engineering", "product_support", "integrations_team", "general_support"]},
                    "sentiment": {"type": "string", "enum": ["calm", "frustrated", "angry", "neutral"]},
                    "summary": {"type": "string"},
                    "recommended_next_action": {"type": "string"}
                },
                "required": ["category", "urgency", "suggested_team", "sentiment", "summary", "recommended_next_action"]
            }
        }],
        tool_choice={"type": "tool", "name": "triage_ticket"},
        messages=[{"role": "user", "content": ticket_text}]
    )
        parsed = response.content[0].input
        triage = TicketTriage(**parsed)
        triage.warnings = generate_warnings(ticket_text, triage)
        return triage

    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")