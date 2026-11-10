from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import customers, llm
from app.config import get_settings
from app.db import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Creates tables added since the last seed (e.g. llm_calls); existing tables are untouched.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="RM Copilot Agent Service", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(llm.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "llm_provider": get_settings().llm_provider}
