"""High-level LLM orchestration for multi-stage chat workflow."""

import json
from pathlib import Path
from typing import Literal, cast

from clan_lib.api import API
from clan_lib.errors import ClanAiError
from clan_lib.flake.flake import Flake
from clan_lib.services.modules import InputName, ServiceReadmeCollection

from .llm_types import ChatResult, NextAction
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
    PendingDiscoveryState,
    PendingFinalDecisionState,
    PendingReadmeFetchState,
    PendingServiceSelectionState,
    ReadmeRequest,
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


@API.register
def get_llm_turn(
    user_request: str,
    flake: Flake,
    conversation_history: ConversationHistory | None = None,
    provider: Literal["openai", "ollama", "claude"] = "ollama",
    trace_file: Path | None = None,
    session_state: SessionState | None = None,
    execute_next_action: bool = False,
) -> ChatResult:
    """High-level API that orchestrates the entire multi-stage chat workflow.

    This function handles the complete flow using a multi-turn approach:
    1. Discovery phase - LLM selects relevant services
    2. Readme fetching - Retrieves detailed documentation
    3. Final decision - LLM makes informed suggestions
    4. Conversion - Transforms suggestions to inventory instances

    Before each expensive operation, the function returns with next_action describing
    what will happen. The caller must call again with execute_next_action=True.

    Args:
        user_request: The user's message/request
        flake: The Flake object to get services from
        conversation_history: Optional list of prior messages in the conversation
        provider: The LLM provider to use
        trace_file: Optional path to write LLM interaction traces for debugging
        session_state: Optional cross-turn state to resume pending workflows
        execute_next_action: If True, execute the pending operation in session_state

    Returns:
        ChatResult containing proposed instances, updated history, next_action, and assistant message

    Example:
        >>> result = process_chat_turn("Set up a web server", flake)
        >>> while result.next_action:
        ...     # Show user what will happen
        ...     print(result.next_action["description"])
        ...     result = process_chat_turn(
        ...         user_request="",
        ...         flake=flake,
        ...         session_state=result.session_state,
        ...         execute_next_action=True
        ...     )

    """
    history = list(conversation_history) if conversation_history else []
    state: SessionState = cast(
        "SessionState", dict(session_state) if session_state else {}
    )

    # Add non-empty user message to history for conversation tracking
    # Phases will also add it to their messages array for LLM calls
    if user_request:
        history.append(_user_message(user_request))

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

    # Check pending states in workflow order (earliest to latest)
    pending_discovery_raw = state.get("pending_discovery")
    pending_discovery: PendingDiscoveryState | None = (
        pending_discovery_raw if isinstance(pending_discovery_raw, dict) else None
    )

    pending_readme_fetch_raw = state.get("pending_readme_fetch")
    pending_readme_fetch: PendingReadmeFetchState | None = (
        pending_readme_fetch_raw if isinstance(pending_readme_fetch_raw, dict) else None
    )

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

        # Only pop if we can't deserialize (invalid state)
        if resume_readme_results is None:
            state.pop("pending_service_selection", None)

    # Handle pending_discovery state: execute discovery if execute_next_action=True
    if pending_discovery is not None and execute_next_action:
        state.pop("pending_discovery", None)
        # Continue to execute discovery below (after pending state checks)

    # Handle pending_readme_fetch state: execute readme fetch if execute_next_action=True
    if pending_readme_fetch is not None and execute_next_action:
        readme_requests_raw = pending_readme_fetch.get("readme_requests", [])
        readme_requests = cast("list[ReadmeRequest]", readme_requests_raw)

        if readme_requests:
            state.pop("pending_readme_fetch", None)
            readme_results = execute_readme_requests(readme_requests, flake)

            # Save readme results and return next_action for service selection
            state["pending_service_selection"] = cast(
                "PendingServiceSelectionState",
                {"readme_results": _serialize_readme_results(readme_results)},
            )
            service_count = len(readme_results)
            next_action_selection: NextAction = {
                "type": "service_selection",
                "description": f"Analyzing {service_count} service(s) to find the best match",
                "estimated_duration_seconds": 15,
                "details": {"service_count": service_count},
            }
            return ChatResult(
                next_action=next_action_selection,
                proposed_instances=(),
                conversation_history=tuple(history),
                assistant_message="",
                requires_user_response=False,
                error=None,
                session_state=_state_copy(),
            )

        state.pop("pending_readme_fetch", None)

    if pending_final is not None:
        service_name = pending_final.get("service_name")
        service_summary = pending_final.get("service_summary")

        if isinstance(service_name, str) and isinstance(service_summary, str):
            if execute_next_action:
                state.pop("pending_final_decision", None)

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

                if function_calls:
                    proposed_instances = llm_final_decision_to_inventory_instances(
                        function_calls
                    )
                    instance_names = [
                        inst["module"]["name"] for inst in proposed_instances
                    ]
                    summary = f"I suggest configuring these services: {', '.join(instance_names)}"
                    history.append(
                        _assistant_message(summary, mode=ASSISTANT_MODE_FINAL)
                    )

                    return ChatResult(
                        next_action=None,
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
                        next_action=None,
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

            # If not executing, return next_action for final decision
            next_action_final_pending: NextAction = {
                "type": "final_decision",
                "description": f"Generating configuration for {service_name}",
                "estimated_duration_seconds": 20,
                "details": {"service_name": service_name},
            }
            return ChatResult(
                next_action=next_action_final_pending,
                proposed_instances=(),
                conversation_history=tuple(history),
                assistant_message="",
                requires_user_response=False,
                error=None,
                session_state=_state_copy(),
            )

        state.pop("pending_final_decision", None)

    def _continue_with_service_selection(
        readme_results: dict[InputName, ServiceReadmeCollection],
    ) -> ChatResult:
        # Extract all service names from readme results
        [
            service_name
            for collection in readme_results.values()
            for service_name in collection.readmes
        ]

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
                next_action=None,
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

        # After service selection, always return next_action for final decision
        state["pending_final_decision"] = cast(
            "PendingFinalDecisionState",
            {
                "service_name": selection_result.selected_service,
                "service_summary": selection_result.service_summary,
            },
        )
        next_action_final: NextAction = {
            "type": "final_decision",
            "description": f"Generating configuration for {selection_result.selected_service}",
            "estimated_duration_seconds": 20,
            "details": {"service_name": selection_result.selected_service},
        }
        return ChatResult(
            next_action=next_action_final,
            proposed_instances=(),
            conversation_history=tuple(history),
            assistant_message="",
            requires_user_response=False,
            error=None,
            session_state=_state_copy(),
        )

    if resume_readme_results is not None:
        if execute_next_action:
            # Pop the pending state now that we're executing
            state.pop("pending_service_selection", None)
            return _continue_with_service_selection(resume_readme_results)

        # If not executing, return next_action for service selection
        service_count = len(resume_readme_results)
        next_action_sel_resume: NextAction = {
            "type": "service_selection",
            "description": f"Analyzing {service_count} service(s) to find the best match",
            "estimated_duration_seconds": 15,
            "details": {"service_count": service_count},
        }
        return ChatResult(
            next_action=next_action_sel_resume,
            proposed_instances=(),
            conversation_history=tuple(history),
            assistant_message="",
            requires_user_response=False,
            error=None,
            session_state=_state_copy(),
        )

    # Stage 1: Discovery phase
    # If we're not executing and have no pending states, return next_action for discovery
    has_pending_states = (
        pending_discovery is not None
        or pending_readme_fetch is not None
        or pending_selection is not None
        or pending_final is not None
    )
    if not execute_next_action and not has_pending_states:
        state["pending_discovery"] = cast("PendingDiscoveryState", {})
        next_action: NextAction = {
            "type": "discovery",
            "description": "Analyzing your request and discovering relevant services",
            "estimated_duration_seconds": 10,
            "details": {"phase": "discovery"},
        }
        return ChatResult(
            next_action=next_action,
            proposed_instances=(),
            conversation_history=tuple(history),
            assistant_message="",
            requires_user_response=False,
            error=None,
            session_state=_state_copy(),
        )

    readme_requests, discovery_message = get_llm_discovery_phase(
        user_request,
        flake,
        conversation_history,
        provider=provider,
        trace_file=trace_file,
        trace_metadata=_metadata(),
    )

    # If LLM asked a question or made a recommendation without readme requests
    if discovery_message and not readme_requests:
        history.append(
            _assistant_message(discovery_message, mode=ASSISTANT_MODE_DISCOVERY)
        )

        return ChatResult(
            next_action=None,
            proposed_instances=(),
            conversation_history=tuple(history),
            assistant_message=discovery_message,
            requires_user_response=True,
            error=None,
            session_state=_state_copy(),
        )

    # If we got readme requests, save them and return next_action for readme fetch
    if readme_requests:
        state["pending_readme_fetch"] = cast(
            "PendingReadmeFetchState",
            {"readme_requests": cast("list[dict[str, JSONValue]]", readme_requests)},
        )
        service_count = len(readme_requests)
        next_action_fetch: NextAction = {
            "type": "fetch_readmes",
            "description": f"Fetching documentation for {service_count} service(s)",
            "estimated_duration_seconds": 5,
            "details": {"service_count": service_count},
        }
        return ChatResult(
            next_action=next_action_fetch,
            proposed_instances=(),
            conversation_history=tuple(history),
            assistant_message="",
            requires_user_response=False,
            error=None,
            session_state=_state_copy(),
        )

    # No readme requests and no message - unexpected
    msg = "LLM did not provide any response or recommendations"
    raise ClanAiError(
        msg,
        description="The LLM should either request service readmes or provide a clarifying message",
        location="Discovery Phase",
    )
