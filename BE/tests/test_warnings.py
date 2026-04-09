import pytest
from app.models.ticket import TicketTriage
from app.services.warnings import generate_warnings


def make_triage(**overrides) -> TicketTriage:
    defaults = {
        "category": "billing",
        "urgency": "medium",
        "suggested_team": "billing_ops",
        "sentiment": "neutral",
        "summary": "Customer was charged twice for the same subscription.",
        "recommended_next_action": "Verify duplicate charge and issue refund.",
    }
    return TicketTriage(**{**defaults, **overrides})


def test_no_warnings_for_clean_ticket():
    triage = make_triage()
    assert generate_warnings("I was charged twice this month.", triage) == []


def test_short_ticket_text_warns():
    triage = make_triage()
    warnings = generate_warnings("Help!", triage)
    assert any("too short" in w for w in warnings)


def test_short_summary_warns():
    triage = make_triage(summary="Bad.")
    warnings = generate_warnings("I was charged twice this month.", triage)
    assert any("Summary" in w for w in warnings)


def test_category_other_warns():
    triage = make_triage(category="other")
    warnings = generate_warnings("Something is broken.", triage)
    assert any("manual review" in w for w in warnings)


def test_critical_urgency_warns():
    triage = make_triage(urgency="critical")
    warnings = generate_warnings("Nobody can log in right now.", triage)
    assert any("Critical" in w for w in warnings)


def test_multiple_warnings_can_stack():
    triage = make_triage(category="other", urgency="critical")
    warnings = generate_warnings("Help!", triage)
    assert len(warnings) >= 3