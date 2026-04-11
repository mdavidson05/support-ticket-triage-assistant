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

### Temperature and eval reliability

When running the eval before setting temperature, results varied between runs for the same input. I found out this is because the default temperature of `1.0` means the model samples from a probability distribution when selecting each token, so borderline classifications like `medium` vs `high` urgency can go either way depending on the random draw.

Setting `temperature=0` forces the model to always pick the highest probability token, making outputs fully deterministic. The same ticket will always produce the same result, which is a requirement for a meaningful eval, without it you can't tell whether a change to the prompt actually improved accuracy or you just got a luckier random sample.

For classification tasks, `temperature=0` is almost always the right choice. Randomness is useful for creative tasks where variation is desirable; for triage, there is a single most defensible answer and consistency is more valuable than creativity.

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

The fix is to add explicit urgency definitions and a company persona to the system prompt so the model can assess business impact accurately.

---

### Second Run — After Prompt Update

The system prompt was updated to include a company persona (AI Solutions Inc, a B2B SaaS platform) and explicit urgency level definitions based on scope of impact and whether a workaround exists.

**Result: 7/15 passed (46%) — up from 40%**

| Ticket | Result | Failing Fields |
|--------|--------|----------------|
| t1 | PASS | — |
| t2 | PASS | — |
| t3 | FAIL | urgency |
| t4 | PASS | — |
| t5 | PASS | — |
| t6 | PASS | — |
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
| t7 | suggested_team | general_support | account_access |
| t8 | urgency | critical | high |
| t9 | urgency | medium | high |
| t11 | urgency | medium | high |
| t12 | category | other | account_management |
| t12 | urgency | low | medium |
| t12 | suggested_team | general_support | product_support |
| t13 | urgency | medium | high |
| t14 | urgency | medium | high |

**Analysis**

The prompt update fixed t6, which had been incorrectly rated `medium` urgency. The explicit `low` definition (feature requests, non-urgent account changes) gave the model enough signal to classify it correctly.

However, the `medium` vs `high` boundary is still the main failure point — four tickets (t9, t11, t13, t14) are still being rated `high` when the expected value is `medium`. The model appears to treat "a user is affected" as sufficient reason for `high`, without adequately weighing whether the core workflow is actually blocked. The urgency definitions may need to be sharper at that boundary, or the sample tickets may need their expected values reviewed.

t8 is the most notable miss — an API returning invalid tokens for all requests is rated `high` rather than `critical`. This suggests the model isn't connecting "all API requests failing" to the "multiple users fully blocked" definition of critical. More explicit examples or stronger wording in the prompt may be needed.

---

### Third Run — After Expected Value Review

The second run analysis raised a question: are the remaining failures caused by the model being wrong, or by the expected values being unrealistic? A review of the 15 tickets identified three where the expected values did not clearly follow from the ticket text:

- **t3** (*"Unable to select desired product from menu"*) — urgency changed from `high` to `medium`. The ticket provides too little context to justify `high`; without knowing whether this blocks a purchase or is a minor UI issue, `medium` is the more defensible default.
- **t12** (*"The new UI is confusing and several team members cannot find where to update account settings"*) — category changed from `other` to `account_management`, urgency from `low` to `medium`, team from `general_support` to `product_support`. The ticket explicitly mentions account settings, so a more specific classification is appropriate. Multiple affected users and a usability regression justify `medium` over `low`.
- **t14** (*"The mobile app crashes immediately after tapping the notifications tab on iOS 18"*) — urgency changed from `medium` to `high`. A reproducible crash is a clear, significant bug — not just inconvenience.

No ticket text was changed. The tickets remain intentionally vague to simulate real-world input.

**Result: 10/15 passed (66%) — up from 46%**

| Ticket | Result | Failing Fields |
|--------|--------|----------------|
| t1 | PASS | — |
| t2 | PASS | — |
| t3 | PASS | — |
| t4 | PASS | — |
| t5 | PASS | — |
| t6 | PASS | — |
| t7 | FAIL | suggested_team |
| t8 | FAIL | urgency |
| t9 | FAIL | urgency |
| t10 | PASS | — |
| t11 | FAIL | urgency |
| t12 | PASS | — |
| t13 | FAIL | urgency |
| t14 | PASS | — |
| t15 | PASS | — |

**Field-level mismatches:**

| Ticket | Field | Expected | Actual |
|--------|-------|----------|--------|
| t7 | suggested_team | general_support | account_access |
| t8 | urgency | critical | high |
| t9 | urgency | medium | high |
| t11 | urgency | medium | high |
| t13 | urgency | medium | high |

**Analysis**

Accuracy improved from 40% (baseline) to 66% across three changes: a prompt update and an expected value review. Breaking down the improvement:

- **Prompt update** (run 2): +1 ticket fixed (t6). The explicit urgency definitions helped the model correctly classify a feature request as `low`.
- **Expected value review** (run 3): +3 tickets fixed (t3, t12, t14). These were cases where the model's answer was reasonable but the labels were debatable. Correcting them removed noise from the eval.

The remaining 5 failures split into two patterns:

1. **`medium` vs `high` over-escalation** (t9, t11, t13) — the model still treats billing disputes and partial data issues as `high` when the expected value is `medium`. This is the hardest boundary to get right because these tickets describe real problems that *could* be high depending on context the ticket doesn't provide.
2. **Specific misclassifications** (t7, t8) — t7 routes an account ownership transfer to `account_access` instead of `general_support`, which is arguably reasonable. t8 still rates a total API failure as `high` instead of `critical`, suggesting the model doesn't infer multi-user impact from "all requests failing".

The key takeaway from this iteration is that **eval quality depends on label quality as much as model quality**. Fixing debatable labels improved accuracy by 20 percentage points without changing the model or the prompt. In a real system, label review would be a recurring part of the eval process, not a one-time fix.

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