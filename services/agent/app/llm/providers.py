from app.llm.base import ChatMessage, LLMResponse


class MockProvider:
    """Deterministic provider for tests and offline demos. Echoes the last user message."""

    name = "mock"

    def __init__(self, model: str = "mock-1") -> None:
        self.model = model

    def complete(self, messages, *, system=None, max_tokens=1024, temperature=0.2) -> LLMResponse:
        last = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return LLMResponse(text=f"[mock] {last}", model=self.model)


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str, model: str) -> None:
        from anthropic import Anthropic  # optional dependency: pip install -e ".[llm]"

        self.client = Anthropic(api_key=api_key)
        self.model = model

    def complete(self, messages, *, system=None, max_tokens=1024, temperature=0.2) -> LLMResponse:
        kwargs = {"system": system} if system else {}
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            **kwargs,
        )
        text = "".join(b.text for b in resp.content if b.type == "text")
        return LLMResponse(
            text=text,
            model=resp.model,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
        )


class OpenAICompatibleProvider:
    """OpenAI, or any OpenAI-compatible endpoint (DeepSeek, Qwen, ...) via base_url."""

    name = "openai"

    def __init__(self, api_key: str, model: str, base_url: str | None = None) -> None:
        from openai import OpenAI  # optional dependency: pip install -e ".[llm]"

        self.client = OpenAI(api_key=api_key, base_url=base_url or None)
        self.model = model

    def complete(self, messages, *, system=None, max_tokens=1024, temperature=0.2) -> LLMResponse:
        msgs: list[dict] = [{"role": "system", "content": system}] if system else []
        msgs += [{"role": m.role, "content": m.content} for m in messages]
        resp = self.client.chat.completions.create(
            model=self.model, messages=msgs, max_tokens=max_tokens, temperature=temperature
        )
        usage = resp.usage
        return LLMResponse(
            text=resp.choices[0].message.content or "",
            model=resp.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )


__all__ = ["ChatMessage", "MockProvider", "AnthropicProvider", "OpenAICompatibleProvider"]
