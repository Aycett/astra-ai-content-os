"""OpenAI LLM provider."""

from app.core.config import get_settings
from app.services.llm.models import LLMRequest, LLMResponse


class OpenAIConfigurationError(RuntimeError):
    """Raised when OpenAI provider is used without required configuration."""


class OpenAIProvider:
    """Generates text using the OpenAI Chat Completions API."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise OpenAIConfigurationError(
                "OPENAI_API_KEY is not configured. Set it in the repository root .env file."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise OpenAIConfigurationError(
                "OpenAI SDK is not installed. Install the openai package to use OpenAIProvider."
            ) from exc

        self._model = model
        self._client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, request: LLMRequest) -> LLMResponse:
        messages: list[dict[str, str]] = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
        )

        text = response.choices[0].message.content or ""

        return LLMResponse(
            text=text,
            provider="openai",
            model=self._model,
            metadata={"request_metadata": request.metadata},
        )
