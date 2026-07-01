"""Mock LLM provider for local development and testing."""

from app.services.llm.models import LLMRequest, LLMResponse


class MockLLMProvider:
    """Returns deterministic text without external API calls."""

    def generate(self, request: LLMRequest) -> LLMResponse:
        system_prefix = (
            f"[system: {request.system_prompt}] "
            if request.system_prompt
            else ""
        )
        text = (
            f"{system_prefix}"
            f"Mock LLM response for prompt: {request.prompt.strip()}"
        )

        return LLMResponse(
            text=text,
            metadata={"request_metadata": request.metadata},
        )
