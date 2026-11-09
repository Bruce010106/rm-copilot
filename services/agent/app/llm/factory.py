from app.config import Settings, get_settings
from app.llm.base import LLMProvider
from app.llm.providers import AnthropicProvider, MockProvider, OpenAICompatibleProvider


def get_provider(settings: Settings | None = None) -> LLMProvider:
    s = settings or get_settings()
    if s.llm_provider == "mock":
        return MockProvider()
    if not s.llm_model:
        raise ValueError("LLM_MODEL must be set when LLM_PROVIDER is not 'mock'")
    if s.llm_provider == "anthropic":
        return AnthropicProvider(api_key=s.anthropic_api_key, model=s.llm_model)
    if s.llm_provider == "openai":
        return OpenAICompatibleProvider(
            api_key=s.openai_api_key, model=s.llm_model, base_url=s.openai_base_url
        )
    raise ValueError(f"unknown LLM_PROVIDER: {s.llm_provider}")
