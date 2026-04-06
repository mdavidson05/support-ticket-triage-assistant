# Support Ticket Triage Assistant

An AI-powered internal support tool that reads raw support tickets and returns structured triage data such as category, urgency, suggested team, sentiment, summary, and recommended next action.

This project is being built as a portfolio project to learn and demonstrate Applied AI engineering skills, especially:

- LLM API integration
- prompt design
- structured JSON output
- schema validation
- retry and error handling
- evaluation of model outputs
- full-stack AI application development

---
# Commands
 - Run Dev Server - uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
## Purpose

Support teams often receive messy, inconsistent free-text tickets. Before a human can act, someone usually needs to:

- understand the issue
- determine urgency
- route it to the right team
- summarize it
- recommend next steps

This project explores how an LLM can help automate that first-pass triage step while still keeping outputs structured, reviewable, and safe for downstream systems.

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

Planned Features
paste ticket text into a UI
send ticket text to a Python backend
call an LLM API to classify and summarize the ticket
return structured JSON
validate the response against a strict schema
retry once if formatting is invalid
display results in a simple frontend
show warnings and validation issues
evaluate performance on a small sample dataset
Scope
In scope for v1
one support ticket at a time
plain text input
one backend triage endpoint
one schema for structured output
one retry path for invalid JSON
a simple frontend
a small local evaluation dataset
local development with Docker and a devcontainer
Out of scope for v1
user authentication
ticketing system integrations
database persistence
batch processing
model fine-tuning
RAG or retrieval
agent workflows
production deployment
Output Schema

The model will return a structured object containing:

category
urgency
suggested_team
sentiment
summary
recommended_next_action
Planned category values
authentication
billing
bug
feature_request
account_management
integration
performance
other
Planned urgency values
low
medium
high
critical
Planned sentiment values
calm
frustrated
angry
neutral
Planned suggested team values
account_access
billing_ops
support_engineering
product_support
integrations_team
general_support
Architecture
High-level architecture
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
Flow
User submits support ticket text
Backend builds a triage prompt
Backend sends the prompt to an LLM API
Model returns structured output
Backend validates the output with Pydantic
If needed, backend retries once for formatting or schema repair
Frontend displays the triage result
Tech Stack
Backend
Python
FastAPI
Pydantic
Frontend
React
TypeScript
AI layer
hosted LLM API
prompt-based structured classification
Dev environment
Docker Desktop
VS Code devcontainer
Project Structure
support-ticket-triage-assistant/
  backend/
    app/
      routes/
      models/
      services/
      prompts/
    data/
      samples/
      logs/
  frontend/
  .devcontainer/
  README.md
  .gitignore
Evaluation Plan

A small evaluation dataset will be created with sample support tickets and expected outputs.

The first evaluation will focus on fields that are easiest to score objectively:

category
urgency
suggested_team

Later evaluation may include:

sentiment
summary quality
recommended next action usefulness
Metrics to track
valid JSON rate
schema validation pass rate
category accuracy
urgency accuracy
suggested team accuracy
retry rate
common failure modes
Development Plan
define the schema
create sample tickets
build a fake backend response first
replace the fake response with a real LLM call
validate output
add retry logic
build the frontend
create an evaluation script
polish and document the project
Design Principles
structured over chatty
honest over complete
validate model output
keep the first version narrow
treat this like a real product component
Planned Milestones
Milestone 1
create repo structure
write README
define triage schema
Milestone 2
create sample ticket dataset
define expected outputs
Milestone 3
build FastAPI app
add health route
add fake triage endpoint
Milestone 4
write prompt template
connect LLM API
return structured triage output
Milestone 5
add schema validation
add retry logic
add warnings for edge cases
Milestone 6
build React frontend
show input and output cleanly
Milestone 7
add evaluation script
measure baseline quality
Milestone 8
polish README
document tradeoffs and limitations
record a demo
Known Limitations
no real ticketing platform integration
no customer or account history
no fine-tuning
no production deployment
output quality depends on prompt design and model behavior
some fields like summary quality are harder to evaluate objectively
Future Improvements
batch triage for multiple tickets
human review flag for uncertain outputs
confidence or ambiguity indicators
integration with a mock ticket queue
editable review UI
analytics dashboard for triage outcomes
model comparison across prompts or providers
Status

Current status: In progress

This README will be updated as the project is built.

### Key Design Decisions

I chose Haiku because classification doesn't require frontier reasoning capability, and it keeps cost and latency low.
However, I later discovered there to be a tradeoff which in the end I was comfortable making. Haiku, given that it was
trained using data from StackOverflow, Github etc that it always uses code fences when returning a JSON output, meaning that 
initially I had to manually strip each response. I was surprised as I had included the instructions and JSON SCHEMA in the Prompt
Template however Haiku can default to it's training pattern despite instruction. The compromise was to remove the instruction 
and JSON schema out of the template and to use tool calling instead, thus avoiding the code fencing issue as the model fills in
a structured input object instead of producing text itself.
