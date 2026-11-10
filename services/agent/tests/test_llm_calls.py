from decimal import Decimal

import pytest
from sqlalchemy import select

from app.config import Settings
from app.llm import ChatMessage, LLMResponse, complete_and_record
from app.llm.pricing import cost_usd
from app.llm.providers import MockProvider
from app.models import LLMCall


class FakeProvider:
    """Stands in for a paid provider: fixed model and token counts, no network."""

    name = "anthropic"

    def __init__(self, model: str = "claude-opus-5-5") -> None:
        self.model = model

    def complete(self, messages, *, system=None, max_tokens=1024, temperature=0.2) -> LLMResponse:
        return LLMResponse(text="ok", model=self.model, input_tokens=1000, output_tokens=500)


class FailingProvider:
    name = "anthropic"
    model = "claude-opus-5-5"

    def complete(self, messages, *, system=None, max_tokens=1024, temperature=0.2) -> LLMResponse:
        raise RuntimeError("rate limited")


MESSAGES = [ChatMessage("user", "你好")]


def test_cost_uses_model_price():
    # 1M input at $4 + 1M output at $20
    assert cost_usd("claude-opus-5-5", 1_000_000, 1_000_000) == Decimal("24.000000")
    assert cost_usd("claude-haiku-5-5", 1000, 500) == Decimal("0.000350")


def test_cost_matches_longest_model_prefix():
    assert cost_usd("claude-opus-5", 1_000_000, 0) == Decimal("5.000000")
    assert cost_usd("claude-opus-5-5", 1_000_000, 0) == Decimal("4.000000")


def test_cost_unknown_model_is_none_unless_price_configured():
    no_price = Settings(llm_price_input_per_mtok=None, llm_price_output_per_mtok=None)
    assert cost_usd("deepseek-chat", 1000, 1000, no_price) is None

    priced = Settings(llm_price_input_per_mtok=0.5, llm_price_output_per_mtok=2)
    assert cost_usd("deepseek-chat", 1_000_000, 1_000_000, priced) == Decimal("2.500000")


def test_mock_call_is_recorded_with_zero_cost(session_factory):
    with session_factory() as s:
        resp = complete_and_record(s, MockProvider(), MESSAGES, purpose="test")
        assert resp.text == "[mock] 你好"

        call = s.scalars(select(LLMCall)).one()
        assert (call.provider, call.model, call.purpose, call.status) == (
            "mock",
            "mock-1",
            "test",
            "ok",
        )
        assert call.cost_usd == 0
        assert call.latency_ms >= 0


def test_every_call_gets_a_row_with_tokens_and_cost(session_factory):
    with session_factory() as s:
        for _ in range(3):
            complete_and_record(s, FakeProvider(), MESSAGES, purpose="customer_summary")

        calls = s.scalars(select(LLMCall)).all()
        assert len(calls) == 3
        assert calls[0].input_tokens == 1000
        assert calls[0].output_tokens == 500
        # 1000 * $4/M + 500 * $20/M
        assert calls[0].cost_usd == Decimal("0.014000")


def test_failed_call_is_recorded_and_reraised(session_factory):
    with session_factory() as s:
        with pytest.raises(RuntimeError):
            complete_and_record(s, FailingProvider(), MESSAGES, purpose="test")

        call = s.scalars(select(LLMCall)).one()
        assert call.status == "error"
        assert call.error == "rate limited"
        assert call.cost_usd is None


def test_usage_endpoint_groups_by_model_and_purpose(client, session_factory):
    with session_factory() as s:
        complete_and_record(s, FakeProvider(), MESSAGES, purpose="customer_summary")
        complete_and_record(s, FakeProvider(), MESSAGES, purpose="customer_summary")
        complete_and_record(s, MockProvider(), MESSAGES, purpose="nl2sql")
        with pytest.raises(RuntimeError):
            complete_and_record(s, FailingProvider(), MESSAGES, purpose="customer_summary")

    body = client.get("/llm/usage").json()
    assert body["total_calls"] == 4
    assert Decimal(body["total_cost_usd"]) == Decimal("0.028")

    top = body["rows"][0]
    assert (top["model"], top["purpose"], top["calls"], top["errors"]) == (
        "claude-opus-5-5",
        "customer_summary",
        3,
        1,
    )
    assert top["input_tokens"] == 2000
    assert top["unpriced_calls"] == 0

    calls = client.get("/llm/calls", params={"limit": 2}).json()
    assert len(calls) == 2
    assert calls[0]["status"] == "error"
