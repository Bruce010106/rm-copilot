"""Single entry point for LLM calls: every call is timed, priced and written to `llm_calls`."""

import time

from sqlalchemy.orm import Session

from app.llm.base import ChatMessage, LLMProvider, LLMResponse
from app.llm.pricing import cost_usd
from app.models import LLMCall


def complete_and_record(
    session: Session,
    provider: LLMProvider,
    messages: list[ChatMessage],
    *,
    purpose: str,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.2,
) -> LLMResponse:
    """Call the provider and log the call. Features must use this, not `provider.complete`.

    `purpose` names the feature making the call (e.g. "customer_summary"). Failed calls are
    logged too, then the error is re-raised. The log row is committed on `session`.
    """
    started = time.perf_counter()
    try:
        resp = provider.complete(
            messages, system=system, max_tokens=max_tokens, temperature=temperature
        )
    except Exception as exc:
        session.add(
            LLMCall(
                provider=provider.name,
                model=getattr(provider, "model", ""),
                purpose=purpose,
                latency_ms=_elapsed_ms(started),
                status="error",
                error=str(exc)[:500],
            )
        )
        session.commit()
        raise

    session.add(
        LLMCall(
            provider=provider.name,
            model=resp.model,
            purpose=purpose,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
            latency_ms=_elapsed_ms(started),
            cost_usd=cost_usd(resp.model, resp.input_tokens, resp.output_tokens),
            status="ok",
        )
    )
    session.commit()
    return resp


def _elapsed_ms(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
