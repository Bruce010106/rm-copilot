from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CustomerSummary(ORM):
    id: str
    name: str
    city: str
    tier: str
    risk_level: str
    aum: Decimal
    rm_id: str
    tags: list[str]


class CustomerPage(BaseModel):
    items: list[CustomerSummary]
    total: int
    page: int
    page_size: int


class HoldingOut(ORM):
    id: str
    product_id: str
    product_name: str
    category: str
    amount: Decimal
    start_date: date
    maturity_date: date | None


class InteractionOut(ORM):
    id: str
    channel: str
    occurred_at: datetime
    content: str


class CustomerDetail(CustomerSummary):
    gender: str
    birth_date: date
    occupation: str
    onboarded_at: date
    rm_name: str
    holdings: list[HoldingOut]
    interactions: list[InteractionOut]


class LLMCallOut(ORM):
    id: int
    created_at: datetime
    provider: str
    model: str
    purpose: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: Decimal | None
    status: str
    error: str | None


class LLMUsageRow(BaseModel):
    provider: str
    model: str
    purpose: str
    calls: int
    errors: int
    unpriced_calls: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    avg_latency_ms: int


class LLMUsage(BaseModel):
    total_calls: int
    total_cost_usd: Decimal
    rows: list[LLMUsageRow]
