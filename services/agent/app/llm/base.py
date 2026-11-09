"""Provider-neutral LLM interface.

Every feature talks to `LLMProvider`, never to a vendor SDK directly, so models can be
swapped and compared (quality / latency / cost) without touching feature code.
"""

from dataclasses import dataclass, field
from typing import Literal, Protocol


@dataclass
class ChatMessage:
    role: Literal["user", "assistant"]
    content: str


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    raw: dict = field(default_factory=dict, repr=False)


class LLMProvider(Protocol):
    name: str

    def complete(
        self,
        messages: list[ChatMessage],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> LLMResponse: ...
