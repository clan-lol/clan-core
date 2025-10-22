"""Type definitions and dataclasses for LLM orchestration."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from clan_lib.nix_models.clan import InventoryInstance

from .schemas import ChatMessage, SessionState


@dataclass(frozen=True)
class DiscoveryProgressEvent:
    """Progress event during discovery phase."""

    service_names: list[str] | None = None
    stage: Literal["discovery"] = "discovery"
    status: Literal["analyzing", "complete"] = "analyzing"


@dataclass(frozen=True)
class ReadmeFetchProgressEvent:
    """Progress event during readme fetching."""

    count: int
    service_names: list[str]
    stage: Literal["readme_fetch"] = "readme_fetch"
    status: Literal["fetching", "complete"] = "fetching"


@dataclass(frozen=True)
class ServiceSelectionProgressEvent:
    """Progress event during service selection phase."""

    service_names: list[str]
    stage: Literal["service_selection"] = "service_selection"
    status: Literal["selecting", "complete"] = "selecting"


@dataclass(frozen=True)
class FinalDecisionProgressEvent:
    """Progress event during final decision phase."""

    stage: Literal["final_decision"] = "final_decision"
    status: Literal["reviewing", "complete"] = "reviewing"


@dataclass(frozen=True)
class ConversationProgressEvent:
    """Progress event for conversation continuation."""

    message: str
    stage: Literal["conversation"] = "conversation"
    awaiting_response: bool = True


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


ProgressEvent = (
    DiscoveryProgressEvent
    | ReadmeFetchProgressEvent
    | ServiceSelectionProgressEvent
    | FinalDecisionProgressEvent
    | ConversationProgressEvent
)

ProgressCallback = Callable[[ProgressEvent], None]


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

    """

    proposed_instances: tuple[InventoryInstance, ...]
    conversation_history: tuple[ChatMessage, ...]
    assistant_message: str
    requires_user_response: bool
    session_state: SessionState
    error: str | None = None


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for an LLM model.

    Attributes:
        name: The model identifier/name
        provider: The LLM provider
        timeout: Request timeout in seconds (default: 120)

    """

    name: str
    provider: Literal["openai", "ollama", "claude"]
    timeout: int = 120


# Default model configurations for each provider
DEFAULT_MODELS: dict[Literal["openai", "ollama", "claude"], ModelConfig] = {
    "openai": ModelConfig(name="gpt-4o", provider="openai", timeout=60),
    "claude": ModelConfig(name="claude-sonnet-4-5", provider="claude", timeout=60),
    "ollama": ModelConfig(name="qwen3:4b-instruct", provider="ollama", timeout=120),
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
