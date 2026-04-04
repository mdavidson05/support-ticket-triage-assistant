from fastapi import FastAPI
from app.routes.triage import router as triage_router

app = FastAPI(title="Support Ticket Triage Assistant")

app.include_router(triage_router)


@app.get("/health")
def health():
    return {"status": "ok"}