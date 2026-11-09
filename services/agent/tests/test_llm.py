import pytest

from app.config import Settings
from app.llm import ChatMessage, get_provider


def test_mock_provider_echoes_last_user_message():
    provider = get_provider(Settings(llm_provider="mock"))
    resp = provider.complete([ChatMessage("user", "你好")])
    assert resp.text == "[mock] 你好"


def test_real_provider_requires_model():
    with pytest.raises(ValueError):
        get_provider(Settings(llm_provider="anthropic", llm_model=""))


def test_unknown_provider():
    with pytest.raises(ValueError):
        get_provider(Settings(llm_provider="nope", llm_model="x"))
