"""High-level API functions for LLM interactions, suitable for HTTP APIs and web UIs.

This module provides a clean, stateless API for integrating LLM functionality into
web applications and HTTP services. It wraps the complex multi-stage workflow into
simple function calls with serializable inputs and outputs.
"""

from pathlib import Path
from typing import Any, Literal, TypedDict, cast

from clan_lib.api import API
from clan_lib.flake.flake import Flake

from .llm import (
    DEFAULT_MODELS,
    ChatResult,
    DiscoveryProgressEvent,
    FinalDecisionProgressEvent,
    ModelConfig,
    ProgressCallback,
    ProgressEvent,
    ReadmeFetchProgressEvent,
    get_model_config,
    process_chat_turn,
)
from .schemas import ChatMessage, ConversationHistory, SessionState


class ChatTurnRequest(TypedDict, total=False):
    """Request payload for a chat turn.

    Attributes:
        user_message: The user's message/request
        conversation_history: Optional list of prior messages in the conversation
        provider: The LLM provider to use (default: "claude")
        trace_file: Optional path to write LLM interaction traces for debugging
        session_state: Opaque state returned from the previous turn

    """

    user_message: str
    conversation_history: ConversationHistory | None
    provider: Literal["openai", "ollama", "claude"]
    trace_file: Path | None
    session_state: SessionState | None


class ChatTurnResponse(TypedDict):
    """Response payload for a chat turn.

    Attributes:
        proposed_instances: List of inventory instances suggested by the LLM
        conversation_history: Updated conversation history after this turn
        assistant_message: Message from the assistant
        requires_user_response: Whether the assistant is waiting for user input
        error: Error message if something went wrong (None on success)
        session_state: State blob to pass into the next turn when continuing the workflow

    """

    proposed_instances: list[dict[str, Any]]
    conversation_history: list[ChatMessage]
    assistant_message: str
    requires_user_response: bool
    error: str | None
    session_state: SessionState


class ProgressEventResponse(TypedDict):
    """Progress event for streaming updates.

    Attributes:
        stage: The current stage of processing
        status: The status within that stage (if applicable)
        count: Count of items (for readme_fetch stage)
        message: Message content (for conversation stage)

    """

    stage: str
    status: str | None
    count: int | None
    message: str | None


@API.register
def get_llm_turn(
    flake: Flake,
    request: ChatTurnRequest,
    progress_callback: ProgressCallback | None = None,
) -> ChatTurnResponse:
    """Process a single chat turn through the LLM workflow.

    This is the main entry point for HTTP APIs and web UIs to interact with
    the LLM functionality. It handles:
    - Service discovery
    - Documentation fetching
    - Final decision making
    - Conversation management

    Args:
        flake: The Flake object representing the clan configuration
        request: The chat turn request containing user message and optional history
        progress_callback: Optional callback for progress updates

    Returns:
        ChatTurnResponse with proposed instances and conversation state

    Example:
        >>> from clan_lib.flake.flake import Flake
        >>> flake = Flake("/path/to/clan")
        >>> request: ChatTurnRequest = {
        ...     "user_message": "Set up a web server",
        ...     "provider": "claude"
        ... }
        >>> response = chat_turn(flake, request)
        >>> if response["proposed_instances"]:
        ...     print("LLM suggests:", response["proposed_instances"])
        >>> if response["requires_user_response"]:
        ...     print("Assistant asks:", response["assistant_message"])

    """
    result: ChatResult = process_chat_turn(
        user_request=request["user_message"],
        flake=flake,
        conversation_history=request.get("conversation_history"),
        provider=request.get("provider", "claude"),
        progress_callback=progress_callback,
        trace_file=request.get("trace_file"),
        session_state=request.get("session_state"),
    )

    # Convert frozen tuples to lists for JSON serialization
    return ChatTurnResponse(
        proposed_instances=[dict(inst) for inst in result.proposed_instances],
        conversation_history=list(result.conversation_history),
        assistant_message=result.assistant_message,
        requires_user_response=result.requires_user_response,
        error=result.error,
        session_state=cast("SessionState", dict(result.session_state)),
    )


def progress_event_to_dict(event: ProgressEvent) -> ProgressEventResponse:
    """Convert a ProgressEvent to a dictionary suitable for JSON serialization.

    This helper function is useful for streaming progress updates over HTTP
    (e.g., Server-Sent Events or WebSockets).

    Args:
        event: The progress event to convert

    Returns:
        Dictionary representation of the event

    Example:
        >>> from clan_lib.llm.llm import DiscoveryProgressEvent
        >>> event = DiscoveryProgressEvent(status="analyzing")
        >>> progress_event_to_dict(event)
        {'stage': 'discovery', 'status': 'analyzing', 'count': None, 'message': None}

    """
    base_response: ProgressEventResponse = {
        "stage": event.stage,
        "status": None,
        "count": None,
        "message": None,
    }

    if isinstance(event, (DiscoveryProgressEvent, FinalDecisionProgressEvent)):
        base_response["status"] = event.status
    elif isinstance(event, ReadmeFetchProgressEvent):
        base_response["status"] = event.status
        base_response["count"] = event.count
    # ConversationProgressEvent has message field
    elif hasattr(event, "message"):
        base_response["message"] = event.message  # type: ignore[attr-defined]
        if hasattr(event, "awaiting_response"):
            base_response["status"] = (
                "awaiting_response"
                if event.awaiting_response  # type: ignore[attr-defined]
                else "complete"
            )

    return base_response


# Re-export types for convenience
__all__ = [
    "DEFAULT_MODELS",
    "ChatTurnRequest",
    "ChatTurnResponse",
    "ModelConfig",
    "ProgressCallback",
    "ProgressEvent",
    "ProgressEventResponse",
    "get_llm_turn",
    "get_model_config",
    "progress_event_to_dict",
]
