from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy import case, func, select

from app.db import SessionDep
from app.models import LLMCall
from app.schemas import LLMCallOut, LLMUsage, LLMUsageRow

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/usage", response_model=LLMUsage)
def usage(session: SessionDep) -> LLMUsage:
    """Calls, tokens and cost grouped by provider / model / purpose."""
    unpriced = LLMCall.cost_usd.is_(None) & (LLMCall.status == "ok")
    stmt = (
        select(
            LLMCall.provider,
            LLMCall.model,
            LLMCall.purpose,
            func.count().label("calls"),
            func.sum(case((LLMCall.status == "error", 1), else_=0)).label("errors"),
            func.sum(case((unpriced, 1), else_=0)).label("unpriced_calls"),
            func.sum(LLMCall.input_tokens).label("input_tokens"),
            func.sum(LLMCall.output_tokens).label("output_tokens"),
            func.coalesce(func.sum(LLMCall.cost_usd), 0).label("cost_usd"),
            func.avg(LLMCall.latency_ms).label("avg_latency_ms"),
        )
        .group_by(LLMCall.provider, LLMCall.model, LLMCall.purpose)
        .order_by(func.count().desc(), LLMCall.model, LLMCall.purpose)
    )
    rows = [
        LLMUsageRow(
            provider=r.provider,
            model=r.model,
            purpose=r.purpose,
            calls=r.calls,
            errors=r.errors,
            unpriced_calls=r.unpriced_calls,
            input_tokens=r.input_tokens,
            output_tokens=r.output_tokens,
            cost_usd=Decimal(str(r.cost_usd)),
            avg_latency_ms=round(r.avg_latency_ms),
        )
        for r in session.execute(stmt)
    ]
    return LLMUsage(
        total_calls=sum(r.calls for r in rows),
        total_cost_usd=sum((r.cost_usd for r in rows), start=Decimal(0)),
        rows=rows,
    )


@router.get("/calls", response_model=list[LLMCallOut])
def recent_calls(
    session: SessionDep, limit: Annotated[int, Query(ge=1, le=200)] = 50
) -> list[LLMCall]:
    """Most recent calls, newest first."""
    return list(session.scalars(select(LLMCall).order_by(LLMCall.id.desc()).limit(limit)))
