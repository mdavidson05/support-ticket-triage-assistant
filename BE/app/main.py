from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.triage import router as triage_router

app = FastAPI(title="Support Ticket Triage Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage_router)

@app.get("/health")
def health():
    return {"status": "ok"}