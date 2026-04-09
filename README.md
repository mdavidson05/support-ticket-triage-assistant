# Support Ticket Triage Assistant

An AI-powered internal support tool that reads raw support tickets and returns structured triage data: category, urgency, suggested team, sentiment, summary, and recommended next action.

This project is being built as a portfolio project to learn and demonstrate applied AI engineering skills, including:

- LLM API integration
- Prompt design
- Structured JSON output
- Schema validation
- Retry and error handling
- Evaluation of model outputs
- Full-stack AI application development

---

## Purpose

Support teams often receive messy, inconsistent free-text tickets. Before a human can act, someone usually needs to understand the issue, determine urgency, route it to the right team, summarize it, and recommend next steps.

This project explores how an LLM can help automate that first-pass triage step while keeping outputs structured, reviewable, and safe for downstream systems.

The goal is not to build a chatbot. The goal is to build a reliable AI-assisted workflow component.

---

## What the App Does

The app accepts a support ticket written in plain text and returns structured triage information.

### Example input

> Customer cannot log in after password reset. They say this is blocking payroll processing and need access restored today.

### Example output

```json
{
  "category": "authentication",
  "urgency": "high",
  "suggested_team": "account_access",
  "sentiment": "frustrated",
  "summary": "Customer cannot log in after a password reset and says the issue is blocking payroll processing.",
  "recommended_next_action": "Prioritize account access investigation and verify the password reset flow."
}
```

---

## Running the App

**Backend**
```bash
cd BE
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd FE
npm run dev -- --host 0.0.0.0
```

**Eval script**
```bash
cd BE
python -m app.eval
```

---

## Output Schema

The model returns a structured object containing:

| Field | Values |
|-------|--------|
| `category` | `authentication` `billing` `bug` `feature_request` `account_management` `integration` `performance` `other` |
| `urgency` | `low` `medium` `high` `critical` |
| `sentiment` | `calm` `frustrated` `angry` `neutral` |
| `suggested_team` | `account_access` `billing_ops` `support_engineering` `product_support` `integrations_team` `general_support` |
| `summary` | Free text — one concise sentence |
| `recommended_next_action` | Free text — practical next step |

---

## Architecture

```
React frontend
      |
      v
FastAPI backend
      |
      v
Prompt builder + LLM client
      |
      v
Pydantic validation layer
      |
      v
Structured response + warnings
```

**Request flow:**
1. User submits support ticket text
2. Backend builds a triage prompt
3. Backend sends the prompt to Claude via the Anthropic API
4. Model returns structured output via tool use
5. Backend validates the output with Pydantic
6. Warnings are generated for edge cases
7. Frontend displays the triage result

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, Pydantic |
| Frontend | React, TypeScript, shadcn/ui |
| AI | Claude Haiku (Anthropic API), tool use for structured output |
| Dev environment | Docker Desktop, VS Code devcontainer |

---

## Scope

**In scope for v1**
- One support ticket at a time
- Plain text input
- One backend triage endpoint
- One schema for structured output
- A simple frontend
- A small local evaluation dataset

**Out of scope for v1**
- User authentication
- Ticketing system integrations
- Database persistence
- Batch processing
- Model fine-tuning
- RAG or retrieval
- Agent workflows
- Production deployment

---

## Key Design Decisions

### Tool use instead of text-based prompting

I chose Claude Haiku because classification doesn't require frontier reasoning capability, and it keeps cost and latency low. However, when prompting Haiku to return JSON as text, it consistently wrapped the output in code fences — a pattern from its training data (StackOverflow, GitHub, etc.) that persisted even when the prompt explicitly instructed otherwise.

The fix was to switch to tool use. Instead of generating text, the model fills in a structured input object defined by a JSON schema. This eliminates the code-fencing problem and removes a wider class of failure modes: malformed JSON, missing required fields, and invalid enum values are all impossible when the model is constrained to a schema. This also removed the need for a retry path and format validation logic.

### Prompt context matters for consistent classification

The initial system prompt was intentionally minimal. The first eval run (see below) revealed that urgency was by far the most inconsistent field. The model had no company context and no explicit definitions for urgency levels, so it applied generic heuristics and tended to over-escalate — presumably because overestimating urgency is safer than underestimating it.

The fix is to add a company persona and explicit urgency criteria to the system prompt, giving the model the context it needs to assess business impact consistently.

---

## Evaluation

The eval script (`BE/app/eval.py`) runs sample tickets through the live model and scores three fields against expected values: `category`, `urgency`, and `suggested_team`.

### First Run — Baseline Results

Run against 15 tickets before any prompt tuning.

**Result: 6/15 passed (40%)**

| Ticket | Result | Failing Fields |
|--------|--------|----------------|
| t1 | PASS | — |
| t2 | PASS | — |
| t3 | FAIL | urgency |
| t4 | PASS | — |
| t5 | PASS | — |
| t6 | FAIL | urgency |
| t7 | FAIL | suggested_team |
| t8 | FAIL | urgency |
| t9 | FAIL | urgency |
| t10 | PASS | — |
| t11 | FAIL | urgency |
| t12 | FAIL | category, urgency, suggested_team |
| t13 | FAIL | urgency |
| t14 | FAIL | urgency |
| t15 | PASS | — |

**Field-level mismatches:**

| Ticket | Field | Expected | Actual |
|--------|-------|----------|--------|
| t3 | urgency | high | medium |
| t6 | urgency | low | medium |
| t7 | suggested_team | general_support | account_access |
| t8 | urgency | critical | high |
| t9 | urgency | medium | high |
| t11 | urgency | medium | high |
| t12 | category | other | feature_request |
| t12 | urgency | low | medium |
| t12 | suggested_team | general_support | product_support |
| t13 | urgency | medium | high |
| t14 | urgency | medium | high |

**Analysis**

Urgency accounts for 8 of the 9 failing tickets. The model consistently skews higher than expected — rating `medium` tickets as `high`, and `low` tickets as `medium`. The root cause is a lack of prompt context: without knowing what the product does or which workflows are business-critical, the model falls back on generic rules of thumb and tends to over-escalate, presumably because overestimating urgency is safer than underestimating it.

The fix is to add explicit urgency definitions and a company persona to the system prompt so the model can assess business impact accurately. See `NEXT_STEPS.md` for the full improvement plan.

---

## Known Limitations

- No real ticketing platform integration
- No customer or account history
- No fine-tuning
- No production deployment
- Output quality depends on prompt design and model behavior
- Some fields (summary quality, recommended action usefulness) are harder to evaluate objectively

---

## Status

**Current status: In progress**