import json
import sys
from pathlib import Path

from app.services.triage_service import triage_ticket_with_llm

TEST_TICKETS_PATH = Path(__file__).parent.parent / "data" / "samples" / "tickets.json"
SCORED_FIELDS = ["category", "urgency", "suggested_team"]


def run_eval():
    tickets = json.loads(TEST_TICKETS_PATH.read_text())

    results = []
    total = len(tickets)
    passed = 0

    for ticket in tickets:
        ticket_id = ticket["ticket_id"]
        expected = ticket["expected"]

        print(f"Running {ticket_id}...", end=" ", flush=True)

        try:
            result = triage_ticket_with_llm(ticket["text"])
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"ticket_id": ticket_id, "error": str(e)})
            continue

        field_results = {}
        ticket_passed = True

        for field in SCORED_FIELDS:
            actual = getattr(result, field)
            expected_val = expected[field]
            match = actual == expected_val
            field_results[field] = {"expected": expected_val, "actual": actual, "match": match}
            if not match:
                ticket_passed = False

        if ticket_passed:
            passed += 1
            print("PASS")
        else:
            mismatches = [f for f, v in field_results.items() if not v["match"]]
            print(f"FAIL ({', '.join(mismatches)})")

        results.append({"ticket_id": ticket_id, "fields": field_results, "pass": ticket_passed})

    print()
    print(f"Results: {passed}/{total} passed ({100 * passed // total}%)")
    print()

    for r in results:
        if "error" in r:
            continue
        if not r["pass"]:
            print(f"  {r['ticket_id']}:")
            for field, v in r["fields"].items():
                if not v["match"]:
                    print(f"    {field}: expected={v['expected']}  actual={v['actual']}")

    return passed == total


if __name__ == "__main__":
    success = run_eval()
    sys.exit(0 if success else 1)