"""High-level LLM orchestration for multi-stage chat workflow."""

import json
from pathlib import Path
from typing import Literal, cast

from clan_lib.errors import ClanAiError
from clan_lib.flake.flake import Flake
from clan_lib.services.modules import InputName, ServiceReadmeCollection

from .llm_types import (
    ChatResult,
    DiscoveryProgressEvent,
    FinalDecisionProgressEvent,
    ProgressCallback,
    ReadmeFetchProgressEvent,
    ServiceSelectionProgressEvent,
)
from .phases import (
    execute_readme_requests,
    get_llm_discovery_phase,
    get_llm_final_decision,
    get_llm_service_selection,
    llm_final_decision_to_inventory_instances,
)
from .schemas import (
    ConversationHistory,
    JSONValue,
    PendingFinalDecisionState,
    PendingServiceSelectionState,
    SessionState,
)
from .utils import (
    ASSISTANT_MODE_DISCOVERY,
    ASSISTANT_MODE_FINAL,
    ASSISTANT_MODE_SELECTION,
    _assistant_message,
    _deserialize_readme_results,
    _serialize_readme_results,
    _user_message,
)


def process_chat_turn(
    user_request: str,
    flake: Flake,
    conversation_history: ConversationHistory | None = None,
    provider: Literal["openai", "ollama", "claude"] = "ollama",
    progress_callback: ProgressCallback | None = None,
    trace_file: Path | None = None,
    session_state: SessionState | None = None,
) -> ChatResult:
    """High-level API that orchestrates the entire multi-stage chat workflow.

    This function handles the complete flow:
    1. Discovery phase - LLM selects relevant services
    2. Readme fetching - Retrieves detailed documentation
    3. Final decision - LLM makes informed suggestions
    4. Conversion - Transforms suggestions to inventory instances

    Args:
        user_request: The user's message/request
        flake: The Flake object to get services from
        conversation_history: Optional list of prior messages in the conversation
        provider: The LLM provider to use
        progress_callback: Optional callback for progress updates
        trace_file: Optional path to write LLM interaction traces for debugging
        session_state: Optional cross-turn state to resume pending workflows

    Returns:
        ChatResult containing proposed instances, updated history, and assistant message

    Example:
        >>> result = process_chat_turn(
        ...     "Set up a web server",
        ...     flake,
        ...     progress_callback=lambda event: print(f"Stage: {event.stage}")
        ... )
        >>> if result.proposed_instances:
        ...     print("LLM suggested:", result.proposed_instances)
        >>> if result.requires_user_response:
        ...     print("Assistant asks:", result.assistant_message)

    """
    history = list(conversation_history) if conversation_history else []
    state: SessionState = cast(
        "SessionState", dict(session_state) if session_state else {}
    )

    def _state_snapshot() -> dict[str, JSONValue]:
        try:
            return json.loads(json.dumps(state))
        except (TypeError, ValueError):
            return dict(state)  # type: ignore[arg-type]

    def _metadata(extra: dict[str, JSONValue] | None = None) -> dict[str, JSONValue]:
        base: dict[str, JSONValue] = {"session_state_before": _state_snapshot()}
        if extra:
            base.update(extra)
        return base

    def _state_copy() -> SessionState:
        return cast("SessionState", dict(state))

    pending_final_raw = state.get("pending_final_decision")
    pending_final: PendingFinalDecisionState | None = (
        pending_final_raw if isinstance(pending_final_raw, dict) else None
    )

    pending_selection_raw = state.get("pending_service_selection")
    pending_selection: PendingServiceSelectionState | None = (
        pending_selection_raw if isinstance(pending_selection_raw, dict) else None
    )
    resume_readme_results: dict[InputName, ServiceReadmeCollection] | None = None
    if pending_selection is not None:
        serialized_results = pending_selection.get("readme_results")
        if serialized_results is not None:
            resume_readme_results = _deserialize_readme_results(serialized_results)

        if resume_readme_results is None:
            state.pop("pending_service_selection", None)
        else:
            state.pop("pending_service_selection", None)

    if pending_final is not None:
        service_name = pending_final.get("service_name")
        service_summary = pending_final.get("service_summary")

        if isinstance(service_name, str) and isinstance(service_summary, str):
            if progress_callback:
                progress_callback(FinalDecisionProgressEvent(status="reviewing"))

            function_calls, final_message = get_llm_final_decision(
                user_request,
                flake,
                service_name,
                service_summary,
                conversation_history,
                provider=provider,
                trace_file=trace_file,
                trace_metadata=_metadata(
                    {
                        "selected_service": service_name,
                        "resume": True,
                    }
                ),
            )

            if progress_callback:
                progress_callback(FinalDecisionProgressEvent(status="complete"))

            history.append(_user_message(user_request))

            if function_calls:
                proposed_instances = llm_final_decision_to_inventory_instances(
                    function_calls
                )
                instance_names = [inst["module"]["name"] for inst in proposed_instances]
                summary = (
                    f"I suggest configuring these services: {', '.join(instance_names)}"
                )
                history.append(_assistant_message(summary, mode=ASSISTANT_MODE_FINAL))
                state.pop("pending_final_decision", None)

                return ChatResult(
                    proposed_instances=tuple(proposed_instances),
                    conversation_history=tuple(history),
                    assistant_message=summary,
                    requires_user_response=False,
                    error=None,
                    session_state=_state_copy(),
                )

            if final_message:
                history.append(
                    _assistant_message(final_message, mode=ASSISTANT_MODE_FINAL)
                )
                state["pending_final_decision"] = cast(
                    "PendingFinalDecisionState",
                    {
                        "service_name": service_name,
                        "service_summary": service_summary,
                    },
                )

                return ChatResult(
                    proposed_instances=(),
                    conversation_history=tuple(history),
                    assistant_message=final_message,
                    requires_user_response=True,
                    error=None,
                    session_state=_state_copy(),
                )

            state.pop("pending_final_decision", None)
            msg = "LLM did not provide any response or recommendations"
            raise ClanAiError(
                msg,
                description="Expected either function calls (configuration) or a clarifying message",
                location="Final Decision Phase (pending)",
            )

        state.pop("pending_final_decision", None)

    def _continue_with_service_selection(
        readme_results: dict[InputName, ServiceReadmeCollection],
    ) -> ChatResult:
        # Extract all service names from readme results
        all_service_names = [
            service_name
            for collection in readme_results.values()
            for service_name in collection.readmes
        ]

        if progress_callback:
            progress_callback(
                ServiceSelectionProgressEvent(
                    service_names=all_service_names, status="selecting"
                )
            )

        selection_result = get_llm_service_selection(
            user_request,
            readme_results,
            conversation_history,
            provider=provider,
            trace_file=trace_file,
            trace_metadata=_metadata(),
        )

        if (
            selection_result.clarifying_message
            and not selection_result.selected_service
        ):
            history.append(_user_message(user_request))
            history.append(
                _assistant_message(
                    selection_result.clarifying_message,
                    mode=ASSISTANT_MODE_SELECTION,
                )
            )
            state["pending_service_selection"] = cast(
                "PendingServiceSelectionState",
                {
                    "readme_results": _serialize_readme_results(readme_results),
                },
            )

            return ChatResult(
                proposed_instances=(),
                conversation_history=tuple(history),
                assistant_message=selection_result.clarifying_message,
                requires_user_response=True,
                error=None,
                session_state=_state_copy(),
            )

        if (
            not selection_result.selected_service
            or not selection_result.service_summary
        ):
            msg = "Failed to select service"
            raise ClanAiError(
                msg,
                description=selection_result.clarifying_message
                or "No service selected and no clarifying message provided",
                location="Service Selection Phase",
            )

        if progress_callback:
            progress_callback(FinalDecisionProgressEvent(status="reviewing"))

        function_calls, final_message = get_llm_final_decision(
            user_request,
            flake,
            selection_result.selected_service,
            selection_result.service_summary,
            conversation_history,
            provider=provider,
            trace_file=trace_file,
            trace_metadata=_metadata(
                {"selected_service": selection_result.selected_service}
            ),
        )

        if progress_callback:
            progress_callback(FinalDecisionProgressEvent(status="complete"))

        if function_calls:
            history.append(_user_message(user_request))

            proposed_instances = llm_final_decision_to_inventory_instances(
                function_calls
            )

            instance_names = [inst["module"]["name"] for inst in proposed_instances]
            summary = (
                f"I suggest configuring these services: {', '.join(instance_names)}"
            )
            history.append(_assistant_message(summary, mode=ASSISTANT_MODE_FINAL))
            state.pop("pending_final_decision", None)

            return ChatResult(
                proposed_instances=tuple(proposed_instances),
                conversation_history=tuple(history),
                assistant_message=summary,
                requires_user_response=False,
                error=None,
                session_state=_state_copy(),
            )

        if final_message:
            history.append(_user_message(user_request))
            history.append(_assistant_message(final_message, mode=ASSISTANT_MODE_FINAL))
            state["pending_final_decision"] = cast(
                "PendingFinalDecisionState",
                {
                    "service_name": selection_result.selected_service,
                    "service_summary": selection_result.service_summary,
                },
            )

            return ChatResult(
                proposed_instances=(),
                conversation_history=tuple(history),
                assistant_message=final_message,
                requires_user_response=True,
                error=None,
                session_state=_state_copy(),
            )

        msg = "LLM did not provide any response or recommendations"
        raise ClanAiError(
            msg,
            description="Expected either function calls (configuration) or a clarifying message after service selection",
            location="Final Decision Phase",
        )

    if resume_readme_results is not None:
        return _continue_with_service_selection(resume_readme_results)

    # Stage 1: Discovery phase
    if progress_callback:
        progress_callback(DiscoveryProgressEvent(status="analyzing"))

    readme_requests, discovery_message = get_llm_discovery_phase(
        user_request,
        flake,
        conversation_history,
        provider=provider,
        trace_file=trace_file,
        trace_metadata=_metadata(),
    )

    if progress_callback:
        selected_services = [req["function_name"] for req in readme_requests]
        progress_callback(
            DiscoveryProgressEvent(
                service_names=selected_services if selected_services else None,
                status="complete",
            )
        )

    # If LLM asked a question or made a recommendation without readme requests
    if discovery_message and not readme_requests:
        history.append(_user_message(user_request))
        history.append(
            _assistant_message(discovery_message, mode=ASSISTANT_MODE_DISCOVERY)
        )

        return ChatResult(
            proposed_instances=(),
            conversation_history=tuple(history),
            assistant_message=discovery_message,
            requires_user_response=True,
            error=None,
            session_state=_state_copy(),
        )

    # If we got readme requests, continue to selecting services
    if readme_requests:
        # Stage 2: Fetch readmes
        service_names = [
            f"{req['function_name']} (from {req['input_name'] or 'built-in'})"
            for req in readme_requests
        ]
        if progress_callback:
            progress_callback(
                ReadmeFetchProgressEvent(
                    count=len(readme_requests),
                    service_names=service_names,
                    status="fetching",
                )
            )

        readme_results = execute_readme_requests(readme_requests, flake)

        if progress_callback:
            progress_callback(
                ReadmeFetchProgressEvent(
                    count=len(readme_requests),
                    service_names=service_names,
                    status="complete",
                )
            )

        return _continue_with_service_selection(readme_results)

    # No readme requests and no message - unexpected
    msg = "LLM did not provide any response or recommendations"
    raise ClanAiError(
        msg,
        description="The LLM should either request service readmes or provide a clarifying message",
        location="Discovery Phase",
    )
