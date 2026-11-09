from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import customers
from app.config import get_settings

app = FastAPI(title="RM Copilot Agent Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_provider": get_settings().llm_provider}
