import json
import sys
import time
from datetime import datetime
from pathlib import Path

from app.services.triage_service import triage_ticket_with_usage

TEST_TICKETS_PATH = Path(__file__).parent.parent / "data" / "samples" / "tickets.json"
EVAL_RESULTS_DIR = Path(__file__).parent.parent / "data" / "eval_results"
SCORED_FIELDS = ["category", "urgency", "suggested_team"]


def save_results(results, passed, total, field_totals, field_passed, usage_totals):
    EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    field_accuracy = {
        f: {"passed": field_passed[f], "total": field_totals[f], "accuracy_pct": 100 * field_passed[f] // field_totals[f]}
        for f in SCORED_FIELDS
    }

    output = {
        "timestamp": timestamp,
        "total": total,
        "passed": passed,
        "accuracy_pct": 100 * passed // total,
        "field_accuracy": field_accuracy,
        "usage": usage_totals,
        "tickets": results,
    }
    path = EVAL_RESULTS_DIR / f"eval_{timestamp}.json"
    path.write_text(json.dumps(output, indent=2))
    print(f"Results saved to {path}")


def run_eval():
    tickets = json.loads(TEST_TICKETS_PATH.read_text())

    results = []
    total = len(tickets)
    passed = 0

    field_passed = {f: 0 for f in SCORED_FIELDS}
    field_totals = {f: 0 for f in SCORED_FIELDS}

    usage_totals = {"input_tokens": 0, "output_tokens": 0, "latencies_ms": []}

    for ticket in tickets:
        ticket_id = ticket["ticket_id"]
        expected = ticket["expected"]

        print(f"Running {ticket_id}...", end=" ", flush=True)

        try:
            start = time.monotonic()
            result, usage = triage_ticket_with_usage(ticket["text"])
            latency_ms = round((time.monotonic() - start) * 1000)
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"ticket_id": ticket_id, "error": str(e)})
            continue

        usage_totals["input_tokens"] += usage["input_tokens"]
        usage_totals["output_tokens"] += usage["output_tokens"]
        usage_totals["latencies_ms"].append(latency_ms)

        field_results = {}
        ticket_passed = True

        for field in SCORED_FIELDS:
            actual = getattr(result, field)
            expected_val = expected[field]
            match = actual == expected_val
            field_results[field] = {"expected": expected_val, "actual": actual, "match": match}
            field_totals[field] += 1
            if match:
                field_passed[field] += 1
            else:
                ticket_passed = False

        if ticket_passed:
            passed += 1
            print("PASS")
        else:
            mismatches = [f for f, v in field_results.items() if not v["match"]]
            print(f"FAIL ({', '.join(mismatches)})")

        results.append({
            "ticket_id": ticket_id,
            "fields": field_results,
            "pass": ticket_passed,
            "latency_ms": latency_ms,
            "usage": usage,
        })

    avg_latency = round(sum(usage_totals["latencies_ms"]) / len(usage_totals["latencies_ms"]))

    print()
    print(f"Results: {passed}/{total} passed ({100 * passed // total}%)")
    print()
    print("Field accuracy:")
    for field in SCORED_FIELDS:
        pct = 100 * field_passed[field] // field_totals[field]
        print(f"  {field}: {field_passed[field]}/{field_totals[field]} ({pct}%)")
    print()
    print(f"Avg latency: {avg_latency}ms")
    print(f"Total tokens: {usage_totals['input_tokens']} in / {usage_totals['output_tokens']} out")
    print()

    for r in results:
        if "error" in r:
            continue
        if not r["pass"]:
            print(f"  {r['ticket_id']}:")
            for field, v in r["fields"].items():
                if not v["match"]:
                    print(f"    {field}: expected={v['expected']}  actual={v['actual']}")

    save_results(results, passed, total, field_totals, field_passed, usage_totals)

    return passed == total


if __name__ == "__main__":
    success = run_eval()
    sys.exit(0 if success else 1)