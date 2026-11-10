"""Model price table and cost calculation.

Prices are USD per million tokens (input, output), Anthropic list prices as of 2026-11.
Models not listed here (e.g. DeepSeek / Qwen through the OpenAI-compatible provider) are
priced with LLM_PRICE_INPUT_PER_MTOK / LLM_PRICE_OUTPUT_PER_MTOK from the environment.
"""

from decimal import Decimal

from app.config import Settings, get_settings

PRICES: dict[str, tuple[str, str]] = {
    "claude-fable-5-2": ("8", "40"),
    "claude-fable-5-1": ("10", "50"),
    "claude-opus-5-5": ("4", "20"),
    "claude-opus-5": ("5", "25"),
    "claude-opus-4-8": ("5", "25"),
    "claude-sonnet-5-5": ("2", "10"),
    "claude-sonnet-5": ("2", "10"),
    "claude-sonnet-4-6": ("3", "15"),
    "claude-haiku-5-5": ("0.10", "0.50"),
    "claude-haiku-4-5": ("1", "5"),
}

_MTOK = Decimal(1_000_000)
_PRECISION = Decimal("0.000001")


def price_for(model: str, settings: Settings | None = None) -> tuple[Decimal, Decimal] | None:
    """Return (input, output) USD per million tokens, or None when the price is unknown."""
    if model.startswith("mock"):
        return Decimal(0), Decimal(0)
    # Longest prefix first, so "claude-opus-5-5" never falls back to the "claude-opus-5" price.
    for key in sorted(PRICES, key=len, reverse=True):
        if model.startswith(key):
            price_in, price_out = PRICES[key]
            return Decimal(price_in), Decimal(price_out)
    s = settings or get_settings()
    if s.llm_price_input_per_mtok is not None and s.llm_price_output_per_mtok is not None:
        return Decimal(str(s.llm_price_input_per_mtok)), Decimal(str(s.llm_price_output_per_mtok))
    return None


def cost_usd(
    model: str, input_tokens: int, output_tokens: int, settings: Settings | None = None
) -> Decimal | None:
    """Cost of one call in USD. None means the model has no known price (not "free")."""
    price = price_for(model, settings)
    if price is None:
        return None
    total = (input_tokens * price[0] + output_tokens * price[1]) / _MTOK
    return total.quantize(_PRECISION)
