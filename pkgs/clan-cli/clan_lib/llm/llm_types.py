"""Type definitions and dataclasses for LLM orchestration."""

from dataclasses import dataclass
from typing import Any, Literal, TypedDict

from clan_lib.nix_models.clan import InventoryInstance

from .schemas import ChatMessage, SessionState


class NextAction(TypedDict):
    """Describes the next expensive operation that will be performed.

    Attributes:
        type: The type of operation (discovery, fetch_readmes, service_selection, final_decision)
        description: Human-readable description of what will happen
        estimated_duration_seconds: Rough estimate of operation duration
        details: Phase-specific information (e.g., service names, count)

    """

    type: Literal["discovery", "fetch_readmes", "service_selection", "final_decision"]
    description: str
    estimated_duration_seconds: int
    details: dict[str, Any]


@dataclass(frozen=True)
class ServiceSelectionResult:
    """Result from service selection step.

    Attributes:
        selected_service: Name of the selected service (None if clarification needed)
        service_summary: LLM-generated summary of the service (None if clarification needed)
        clarifying_message: Clarifying question from LLM (empty string if service selected)

    """

    selected_service: str | None
    service_summary: str | None
    clarifying_message: str


@dataclass(frozen=True)
class ChatResult:
    """Result of a complete chat turn through the multi-stage workflow.

    Attributes:
        proposed_instances: List of inventory instances suggested by the LLM (empty if none)
        conversation_history: Updated conversation history after this turn
        assistant_message: Message from the assistant (questions, recommendations, or diff preview)
        requires_user_response: True if the assistant asked a question and needs a response
        error: Error message if something went wrong (None on success)
        session_state: Serializable state to pass into the next turn when continuing a workflow
        next_action: Description of the next operation to be performed (None if workflow complete)

    """

    proposed_instances: tuple[InventoryInstance, ...]
    conversation_history: tuple[ChatMessage, ...]
    assistant_message: str
    requires_user_response: bool
    session_state: SessionState
    next_action: NextAction | None
    error: str | None = None


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for an LLM model.

    Attributes:
        name: The model identifier/name
        provider: The LLM provider
        timeout: Request timeout in seconds (default: 120)
        temperature: Sampling temperature for the model (default: None = use API default)

    """

    name: str
    provider: Literal["openai", "ollama", "claude"]
    timeout: int = 120
    temperature: float | None = None


# Default model configurations for each provider
DEFAULT_MODELS: dict[Literal["openai", "ollama", "claude"], ModelConfig] = {
    "openai": ModelConfig(name="gpt-4o", provider="openai", timeout=60),
    "claude": ModelConfig(name="claude-sonnet-4-5", provider="claude", timeout=60),
    "ollama": ModelConfig(name="qwen3:4b-instruct", provider="ollama", timeout=180),
}


def get_model_config(
    provider: Literal["openai", "ollama", "claude"],
) -> ModelConfig:
    """Get the default model configuration for a provider.

    Args:
        provider: The LLM provider name

    Returns:
        ModelConfig for the specified provider

    """
    return DEFAULT_MODELS[provider]
