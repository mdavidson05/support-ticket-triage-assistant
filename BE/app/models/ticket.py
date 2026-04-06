from pydantic import BaseModel
from typing import Literal


class TicketTriage(BaseModel):
    category: Literal[
        "authentication",
        "billing",
        "bug",
        "feature_request",
        "account_management",
        "integration",
        "performance",
        "other",
    ]
    urgency: Literal["low", "medium", "high", "critical"]
    suggested_team: Literal[
        "account_access",
        "billing_ops",
        "support_engineering",
        "product_support",
        "integrations_team",
        "general_support",
    ]
    sentiment: Literal["calm", "frustrated", "angry", "neutral"]
    summary: str
    recommended_next_action: str
    warnings: list[str] = []