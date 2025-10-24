"""Unit tests for process_chat_turn using mocked endpoints from mytrace.json."""

import json
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import MagicMock, patch

import pytest
from clan_lib.errors import ClanAiError
from clan_lib.flake.flake import Flake
from clan_lib.llm.endpoints import (
    FunctionCallType,
    OllamaChatResponse,
    OpenAIChatCompletionResponse,
    parse_ollama_response,
    parse_openai_response,
)
from clan_lib.llm.llm_types import ServiceSelectionResult
from clan_lib.llm.orchestrator import get_llm_turn
from clan_lib.llm.phases import (
    execute_readme_requests,
    get_llm_final_decision,
    get_llm_service_selection,
)
from clan_lib.llm.schemas import (
    AiAggregate,
    MachineDescription,
    ReadmeRequest,
    SessionState,
    TagDescription,
)
from clan_lib.services.modules import ServiceReadmeCollection

if TYPE_CHECKING:
    from clan_lib.llm.llm_types import ChatResult
    from clan_lib.llm.schemas import ChatMessage


def execute_multi_turn_workflow(
    user_request: str,
    flake: Flake,
    conversation_history: list["ChatMessage"] | None = None,
    provider: str = "claude",
    session_state: SessionState | None = None,
) -> "ChatResult":
    """Execute the multi-turn workflow, auto-executing all pending operations.

    This simulates the behavior of the CLI auto-execute loop in workflow.py.
    """
    result = get_llm_turn(
        user_request=user_request,
        flake=flake,
        conversation_history=conversation_history,
        provider=provider,  # type: ignore[arg-type]
        session_state=session_state,
        execute_next_action=False,
    )

    # Auto-execute any pending operations
    while result.next_action:
        result = get_llm_turn(
            user_request="",
            flake=flake,
            conversation_history=list(result.conversation_history),
            provider=provider,  # type: ignore[arg-type]
            session_state=result.session_state,
            execute_next_action=True,
        )

    return result


@pytest.fixture
def trace_data() -> list[dict[str, Any]]:
    """Load trace data from mytrace.json."""
    trace_file = Path(__file__).parent / "container_data" / "test_trace_data.json"
    with trace_file.open() as f:
        return json.load(f)


@pytest.fixture
def mock_flake() -> MagicMock:
    """Create a mock Flake object with test data."""
    return MagicMock(spec=Flake)
    # Add any necessary attributes or methods the test needs


@pytest.fixture(autouse=True)
def mock_schema_aggregators() -> Generator[None]:
    """Mock the schema aggregation functions to avoid complex setup."""
    machines = [
        MachineDescription(name="gchq-local", description=None),
        MachineDescription(name="qube-email", description=None),
        MachineDescription(name="wintux", description=None),
    ]
    tags = [
        TagDescription(name="all", description="A group containing all machines"),
        TagDescription(
            name="nixos", description="A group containing all NixOS machines"
        ),
        TagDescription(
            name="darwin", description="A group containing all macOS machines"
        ),
    ]

    mock_aggregate: AiAggregate = AiAggregate(
        machines=machines,
        tags=tags,
        tools=[],  # Empty tools list since we're mocking the API calls anyway
    )

    with (
        patch(
            "clan_lib.llm.phases.aggregate_openai_function_schemas",
            return_value=mock_aggregate,
        ),
        patch(
            "clan_lib.llm.phases.aggregate_ollama_function_schemas",
            return_value=mock_aggregate,
        ),
        patch("clan_lib.llm.phases.create_simplified_service_schemas", return_value=[]),
        patch("clan_lib.llm.phases.create_get_readme_tool", return_value={}),
    ):
        yield


def create_openai_response(
    function_calls: list[dict[str, Any]], message: str
) -> OpenAIChatCompletionResponse:
    """Create an OpenAI-compatible response from function calls and message."""
    tool_calls = []
    for i, call in enumerate(function_calls):
        tool_calls.append(
            {
                "id": f"call_{i}",
                "type": "function",
                "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["arguments"]),
                },
            }
        )

    # Cast to the expected type since we're creating a minimal response for testing
    return cast(
        "OpenAIChatCompletionResponse",
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": message,
                        "tool_calls": tool_calls if tool_calls else None,
                    },
                }
            ],
        },
    )


class TestProcessChatTurn:
    """Test process_chat_turn with mocked API responses from trace data."""

    def test_discovery_phase(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test the discovery phase with VPN query."""
        # Get the first trace entry (discovery phase)
        discovery_trace = trace_data[0]
        assert discovery_trace["stage"] == "discovery"

        response_data = discovery_trace["response"]
        function_calls = response_data["function_calls"]
        message = response_data["message"]

        # Create OpenAI-compatible response
        openai_response = create_openai_response(function_calls, message)

        # Mock the Claude API call
        with (
            patch(
                "clan_lib.llm.phases.call_claude_api", return_value=openai_response
            ) as mock_call,
            patch("clan_lib.llm.orchestrator.execute_readme_requests") as mock_execute,
            patch(
                "clan_lib.llm.orchestrator.get_llm_service_selection"
            ) as mock_selection,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
        ):
            # Mock readme results
            mock_execute.return_value = {
                None: MagicMock(
                    input_name=None,
                    readmes={
                        "wireguard": "# Wireguard README",
                        "zerotier": "# ZeroTier README",
                        "mycelium": "# Mycelium README",
                        "yggdrasil": "# Yggdrasil README",
                    },
                )
            }

            # Mock the service selection phase - this should return early with clarifying message
            service_selection_trace = trace_data[1]
            mock_selection.return_value = ServiceSelectionResult(
                selected_service=None,
                service_summary=None,
                clarifying_message=service_selection_trace["response"]["message"],
            )

            # Mock final decision (shouldn't be called, but mock it anyway for safety)
            mock_final.return_value = ([], "")

            # Run multi-turn workflow
            result = execute_multi_turn_workflow(
                user_request="What VPNs are available?",
                flake=mock_flake,
                conversation_history=None,
                provider="claude",
            )

            # Verify the discovery call was made
            assert mock_call.called

            # Verify readme execution was called
            assert mock_execute.called

            # Verify service selection was called
            assert mock_selection.called

            # Final decision should NOT be called since we return early with clarifying message
            assert not mock_final.called

            # Verify the result
            assert result.requires_user_response is True
            assert "VPN" in result.assistant_message
            assert len(result.conversation_history) > 0

    def test_service_selection_with_user_choice(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test service selection when user makes a choice."""
        # Get the trace entry where user selects zerotier
        selection_trace = trace_data[2]
        assert selection_trace["stage"] == "select_service"

        response_data = selection_trace["response"]
        function_calls = response_data["function_calls"]
        assert len(function_calls) == 1
        assert function_calls[0]["name"] == "select_service"

        # Build conversation history up to this point
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {
                "role": "assistant",
                "content": trace_data[1]["response"]["message"],
            },
        ]

        # Create session state with pending service selection (resuming workflow)
        session_state: SessionState = cast(
            "SessionState",
            {
                "pending_service_selection": {
                    "readme_results": [
                        {
                            "input_name": None,
                            "readmes": {
                                "wireguard": "# Wireguard README",
                                "zerotier": "# ZeroTier README",
                                "mycelium": "# Mycelium README",
                                "yggdrasil": "# Yggdrasil README",
                            },
                        }
                    ]
                }
            },
        )

        # Mock the service selection and final decision
        with (
            patch(
                "clan_lib.llm.orchestrator.get_llm_service_selection"
            ) as mock_selection,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
        ):
            mock_selection.return_value = ServiceSelectionResult(
                selected_service="zerotier",
                service_summary=function_calls[0]["arguments"]["summary"],
                clarifying_message="",
            )

            # Mock the final decision phase to ask a question
            final_trace = trace_data[3]
            mock_final.return_value = (
                [],
                final_trace["response"]["message"],
            )

            # Run multi-turn workflow with session state
            result = execute_multi_turn_workflow(
                user_request="Hmm zerotier please",
                flake=mock_flake,
                conversation_history=conversation_history,
                provider="claude",
                session_state=session_state,
            )

            # Verify service selection was called
            assert mock_selection.called

            # Verify final decision was called
            assert mock_final.called

            # Verify the result
            assert result.requires_user_response is True
            assert "controller" in result.assistant_message.lower()

    def test_final_decision_with_configuration(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test final decision phase with actual configuration."""
        # Get the last trace entry (final decision with configuration)
        final_trace = trace_data[-1]
        assert final_trace["stage"] == "final_decision"

        response_data = final_trace["response"]
        function_calls = response_data["function_calls"]
        assert len(function_calls) == 1
        assert function_calls[0]["name"] == "zerotier"

        # Build full conversation history
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {
                "role": "assistant",
                "content": trace_data[1]["response"]["message"],
            },
            {"role": "user", "content": "Hmm zerotier please"},
            {
                "role": "assistant",
                "content": trace_data[3]["response"]["message"],
            },
            {"role": "user", "content": "what is a moon?"},
            {
                "role": "assistant",
                "content": trace_data[4]["response"]["message"],
            },
        ]

        # Mock with pending state
        session_state: SessionState = cast(
            "SessionState",
            {
                "pending_final_decision": {
                    "service_name": "zerotier",
                    "service_summary": trace_data[2]["response"]["function_calls"][0][
                        "arguments"
                    ]["summary"],
                }
            },
        )

        # Mock the final decision call
        with patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final:
            mock_final.return_value = (
                [
                    FunctionCallType(
                        id="call_0",
                        call_id="call_0",
                        type="function_call",
                        name=function_calls[0]["name"],
                        arguments=json.dumps(function_calls[0]["arguments"]),
                    )
                ],
                "",
            )

            # Run multi-turn workflow
            result = execute_multi_turn_workflow(
                user_request="okay then gchq-local as controller and qube-email as moon please everything else as peer",
                flake=mock_flake,
                conversation_history=conversation_history,
                provider="claude",
                session_state=session_state,
            )

            # Verify final decision was called
            assert mock_final.called

            # Verify the result
            assert result.requires_user_response is False
            assert len(result.proposed_instances) == 1
            instance = result.proposed_instances[0]
            assert instance["module"]["name"] == "zerotier"
            assert "controller" in instance["roles"]
            assert "moon" in instance["roles"]
            assert "peer" in instance["roles"]
            assert "gchq-local" in instance["roles"]["controller"]["machines"]
            assert "qube-email" in instance["roles"]["moon"]["machines"]
            assert "wintux" in instance["roles"]["peer"]["machines"]

    def test_conversation_state_progression(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test that conversation state properly progresses between turns."""
        # Test Turn 1: Discovery phase
        discovery_response = create_openai_response(
            trace_data[0]["response"]["function_calls"],
            trace_data[0]["response"]["message"],
        )

        with (
            patch(
                "clan_lib.llm.phases.call_claude_api", return_value=discovery_response
            ),
            patch("clan_lib.llm.orchestrator.execute_readme_requests") as mock_exec,
            patch(
                "clan_lib.llm.orchestrator.get_llm_service_selection"
            ) as mock_selection,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
        ):
            mock_exec.return_value = {
                None: MagicMock(
                    input_name=None,
                    readmes={
                        "wireguard": "README",
                        "zerotier": "README",
                        "mycelium": "README",
                        "yggdrasil": "README",
                    },
                )
            }
            mock_selection.return_value = ServiceSelectionResult(
                selected_service=None,
                service_summary=None,
                clarifying_message=trace_data[1]["response"]["message"],
            )
            mock_final.return_value = ([], "")

            result1 = execute_multi_turn_workflow(
                user_request="What VPNs are available?",
                flake=mock_flake,
                provider="claude",
            )

            # Verify final decision was not called (since we get clarifying message)
            assert not mock_final.called

            # Verify discovery completed and service selection asked clarifying question
            assert result1.requires_user_response is True
            assert "VPN" in result1.assistant_message
            # Session state should have pending_service_selection (with readme results)
            assert "pending_service_selection" in result1.session_state

        # Test Turn 2: Continue with session state
        with (
            patch(
                "clan_lib.llm.orchestrator.get_llm_service_selection"
            ) as mock_selection,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
        ):
            mock_selection.return_value = ServiceSelectionResult(
                selected_service="zerotier",
                service_summary=trace_data[2]["response"]["function_calls"][0][
                    "arguments"
                ]["summary"],
                clarifying_message="",
            )
            mock_final.return_value = ([], trace_data[3]["response"]["message"])

            result2 = execute_multi_turn_workflow(
                user_request="Hmm zerotier please",
                flake=mock_flake,
                conversation_history=list(result1.conversation_history),
                provider="claude",
                session_state=result1.session_state,
            )

            # Verify we progressed to final decision phase
            assert result2.requires_user_response is True
            assert "pending_final_decision" in result2.session_state
            # Conversation history should have grown
            assert len(result2.conversation_history) > len(result1.conversation_history)

    def test_final_message_branch_sets_pending_state(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test that final_message branch properly sets pending_final_decision state."""
        # Build conversation history up to service selection complete
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {"role": "assistant", "content": trace_data[1]["response"]["message"]},
            {"role": "user", "content": "Hmm zerotier please"},
        ]

        # Mock session state with selected service
        session_state: SessionState = cast(
            "SessionState",
            {
                "pending_service_selection": {
                    "readme_results": [
                        {
                            "input_name": None,
                            "readmes": {"zerotier": "# ZeroTier README"},
                        }
                    ]
                }
            },
        )

        # Use trace entry where LLM asks clarifying question in final decision
        clarify_trace = trace_data[3]
        assert len(clarify_trace["response"]["function_calls"]) == 0
        assert clarify_trace["response"]["message"] != ""

        # Mock to return a service selection, then a clarifying message in final decision
        with (
            patch(
                "clan_lib.llm.orchestrator.get_llm_service_selection"
            ) as mock_selection,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
        ):
            mock_selection.return_value = ServiceSelectionResult(
                selected_service="zerotier",
                service_summary="ZeroTier is a mesh VPN...",
                clarifying_message="",
            )
            # Return empty function_calls but with a clarifying message
            mock_final.return_value = ([], clarify_trace["response"]["message"])

            result = execute_multi_turn_workflow(
                user_request="Set up zerotier with gchq-local as controller",
                flake=mock_flake,
                conversation_history=conversation_history,
                provider="claude",
                session_state=session_state,
            )

            # Verify the final_message branch was taken
            assert result.requires_user_response is True
            assert result.assistant_message == clarify_trace["response"]["message"]
            # Verify pending_final_decision state is set
            assert "pending_final_decision" in result.session_state
            assert (
                result.session_state["pending_final_decision"]["service_name"]
                == "zerotier"
            )
            assert result.session_state["pending_final_decision"]["service_summary"]
            # No proposed instances yet
            assert len(result.proposed_instances) == 0

    def test_discovery_message_without_readme_requests(
        self, mock_flake: MagicMock
    ) -> None:
        """Test discovery phase when LLM responds with message but no README requests."""
        # Create a response with a message but no get_readme function calls
        discovery_message = "I need more information about your network setup. Do you have any machines with static public IP addresses?"
        response = create_openai_response([], discovery_message)

        with (
            patch("clan_lib.llm.phases.call_claude_api", return_value=response),
            patch(
                "clan_lib.llm.phases.create_simplified_service_schemas"
            ) as mock_simplified,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
        ):
            mock_simplified.return_value = [
                {
                    "name": "wireguard",
                    "description": "WireGuard VPN",
                    "input": None,
                },
                {
                    "name": "zerotier",
                    "description": "ZeroTier mesh VPN",
                    "input": None,
                },
            ]
            mock_final.return_value = ([], "")

            result = execute_multi_turn_workflow(
                user_request="I want to set up a VPN",
                flake=mock_flake,
                provider="claude",
            )

            # Verify final decision was not called (discovery message without readmes)
            assert not mock_final.called

            # Verify the discovery_message without readme_requests branch
            assert result.requires_user_response is True
            assert result.assistant_message == discovery_message
            # No pending state should be set (discovery is asking for clarification)
            assert "pending_service_selection" not in result.session_state
            assert "pending_final_decision" not in result.session_state
            # No proposed instances
            assert len(result.proposed_instances) == 0
            # Conversation history should contain the exchange
            assert len(result.conversation_history) == 2
            assert result.conversation_history[0]["role"] == "user"
            assert result.conversation_history[1]["role"] == "assistant"

    def test_function_calls_in_service_selection(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test when LLM provides configuration directly after service selection."""
        # Use the final trace entry with zerotier configuration
        final_trace = trace_data[-1]
        function_calls = final_trace["response"]["function_calls"]
        assert len(function_calls) == 1

        # Mock session state with pending service selection
        session_state: SessionState = cast(
            "SessionState",
            {
                "pending_service_selection": {
                    "readme_results": [
                        {
                            "input_name": None,
                            "readmes": {"zerotier": "# ZeroTier README"},
                        }
                    ]
                }
            },
        )

        # Build conversation history
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {"role": "assistant", "content": "Here are the available VPNs..."},
        ]

        # Mock to select service and immediately provide configuration
        with (
            patch(
                "clan_lib.llm.orchestrator.get_llm_service_selection"
            ) as mock_selection,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
            patch("clan_lib.llm.phases.aggregate_ollama_function_schemas") as mock_agg,
        ):
            mock_selection.return_value = ServiceSelectionResult(
                selected_service="zerotier",
                service_summary="ZeroTier mesh VPN",
                clarifying_message="",
            )

            # Return function calls (configuration) without asking questions
            mock_final.return_value = (
                [
                    FunctionCallType(
                        id="call_0",
                        call_id="call_0",
                        type="function_call",
                        name="zerotier",
                        arguments=json.dumps(function_calls[0]["arguments"]),
                    )
                ],
                "",  # No message, just configuration
            )

            mock_agg.return_value = MagicMock(
                tools=[
                    {
                        "type": "function",
                        "function": {"name": "zerotier", "description": "ZeroTier VPN"},
                    }
                ]
            )

            result = execute_multi_turn_workflow(
                user_request="Use zerotier with gchq-local as controller, qube-email as moon, rest as peers",
                flake=mock_flake,
                conversation_history=conversation_history,
                provider="claude",
                session_state=session_state,
            )

            # Verify service selection was called
            assert mock_selection.called

            # Verify final decision was called
            assert mock_final.called

            # Verify the function_calls branch in _continue_with_service_selection
            assert result.requires_user_response is False
            assert len(result.proposed_instances) == 1
            assert result.proposed_instances[0]["module"]["name"] == "zerotier"
            # Should have configuration in roles
            args = result.proposed_instances[0]["roles"]
            assert "controller" in args
            assert "moon" in args
            assert "peer" in args
            # No error
            assert result.error is None


class TestGetLlmServiceSelection:
    """Test get_llm_service_selection with mocked API responses from trace data."""

    def test_service_selection_with_readmes(
        self, trace_data: list[dict[str, Any]]
    ) -> None:
        """Test service selection phase with README data."""
        # Use trace entry for service selection (stage: select_service)
        selection_trace = trace_data[2]
        assert selection_trace["stage"] == "select_service"

        # Create README results from trace data
        readme_results: dict[str | None, ServiceReadmeCollection] = {
            None: ServiceReadmeCollection(
                input_name=None,
                readmes={
                    "wireguard": "# Wireguard VPN\nA fast VPN...",
                    "zerotier": "# ZeroTier\nA mesh VPN...",
                    "mycelium": "# Mycelium\nOverlay network...",
                    "yggdrasil": "# Yggdrasil\nDecentralized routing...",
                },
            )
        }

        # Build conversation history up to this point
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {
                "role": "assistant",
                "content": trace_data[1]["response"]["message"],
            },
        ]

        # Create expected response with select_service call
        function_calls = selection_trace["response"]["function_calls"]
        response = create_openai_response(function_calls, "")

        # Mock the API call
        with patch("clan_lib.llm.phases.call_claude_api", return_value=response):
            result = get_llm_service_selection(
                user_request="Hmm zerotier please",
                readme_results=readme_results,
                conversation_history=conversation_history,
                provider="claude",
            )

            # Verify the result
            assert result.selected_service == "zerotier"
            assert result.service_summary is not None
            assert "controller" in result.service_summary.lower()
            assert result.clarifying_message == ""

    def test_service_selection_asks_clarifying_question(
        self, trace_data: list[dict[str, Any]]
    ) -> None:
        """Test service selection when LLM asks for clarification."""
        # Use trace entry where LLM asks clarifying question (stage: select_service)
        clarify_trace = trace_data[1]
        assert clarify_trace["stage"] == "select_service"
        # Verify this is a clarification (no function calls, has message)
        assert len(clarify_trace["response"]["function_calls"]) == 0
        assert clarify_trace["response"]["message"] != ""

        # Create README results
        readme_results: dict[str | None, ServiceReadmeCollection] = {
            None: ServiceReadmeCollection(
                input_name=None,
                readmes={
                    "wireguard": "# Wireguard README",
                    "zerotier": "# ZeroTier README",
                    "mycelium": "# Mycelium README",
                    "yggdrasil": "# Yggdrasil README",
                },
            )
        }

        # No function calls, just a message
        response = create_openai_response([], clarify_trace["response"]["message"])

        # Mock the API call
        with patch("clan_lib.llm.phases.call_claude_api", return_value=response):
            result = get_llm_service_selection(
                user_request="What VPNs are available?",
                readme_results=readme_results,
                provider="claude",
            )

            # Verify the result - should be a clarifying question
            assert result.selected_service is None
            assert result.service_summary is None
            assert result.clarifying_message != ""
            assert "VPN" in result.clarifying_message


class TestGetLlmFinalDecision:
    """Test get_llm_final_decision with mocked API responses from trace data."""

    def test_final_decision_with_configuration(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test final decision phase with service configuration."""
        # Use the last trace entry (final decision with configuration)
        final_trace = trace_data[-1]
        assert final_trace["stage"] == "final_decision"

        response_data = final_trace["response"]
        function_calls = response_data["function_calls"]
        assert len(function_calls) == 1
        assert function_calls[0]["name"] == "zerotier"

        # Build conversation history
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {"role": "assistant", "content": trace_data[1]["response"]["message"]},
            {"role": "user", "content": "Hmm zerotier please"},
            {"role": "assistant", "content": trace_data[3]["response"]["message"]},
            {"role": "user", "content": "what is a moon?"},
            {"role": "assistant", "content": trace_data[4]["response"]["message"]},
        ]

        # Mock the schema lookup to return zerotier schema
        mock_schema = {
            "type": "function",
            "function": {
                "name": "zerotier",
                "description": "ZeroTier VPN configuration",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "roles": {"type": "object"},
                    },
                },
            },
        }

        # Create response with zerotier function call
        response = create_openai_response(function_calls, "")

        # Mock API and schema aggregation
        with (
            patch("clan_lib.llm.phases.aggregate_ollama_function_schemas") as mock_agg,
            patch("clan_lib.llm.phases.call_claude_api", return_value=response),
        ):
            mock_agg.return_value = MagicMock(tools=[mock_schema])

            function_call_results, message = get_llm_final_decision(
                user_request="okay then gchq-local as controller and qube-email as moon please everything else as peer",
                flake=mock_flake,
                selected_service="zerotier",
                service_summary="ZeroTier is a mesh VPN...",
                conversation_history=conversation_history,
                provider="claude",
            )

            # Verify the result
            assert len(function_call_results) == 1
            assert function_call_results[0]["name"] == "zerotier"
            # Parse the arguments to verify structure
            args = json.loads(function_call_results[0]["arguments"])
            assert "roles" in args
            assert "controller" in args["roles"]
            assert "moon" in args["roles"]
            assert "peer" in args["roles"]

    def test_final_decision_asks_clarifying_question(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test final decision when LLM asks for more information."""
        # Use trace entry where LLM asks about moon (stage: final_decision)
        clarify_trace = trace_data[3]
        assert clarify_trace["stage"] == "final_decision"
        # Verify this is a clarification (no function calls, has message)
        assert len(clarify_trace["response"]["function_calls"]) == 0
        assert clarify_trace["response"]["message"] != ""

        # Build conversation history
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {"role": "assistant", "content": trace_data[1]["response"]["message"]},
            {"role": "user", "content": "Hmm zerotier please"},
        ]

        # Mock schema
        mock_schema = {
            "type": "function",
            "function": {
                "name": "zerotier",
                "description": "ZeroTier VPN",
            },
        }

        # No function calls, just a clarifying message
        response = create_openai_response([], clarify_trace["response"]["message"])

        # Mock API and schema aggregation
        with (
            patch("clan_lib.llm.phases.aggregate_ollama_function_schemas") as mock_agg,
            patch("clan_lib.llm.phases.call_claude_api", return_value=response),
        ):
            mock_agg.return_value = MagicMock(tools=[mock_schema])

            function_call_results, message = get_llm_final_decision(
                user_request="gchq-local as controller please",
                flake=mock_flake,
                selected_service="zerotier",
                service_summary="ZeroTier is a mesh VPN...",
                conversation_history=conversation_history,
                provider="claude",
            )

            # Verify the result - should be a clarifying question
            assert len(function_call_results) == 0
            assert message != ""
            assert "controller" in message.lower()


class TestExecuteReadmeRequests:
    """Test execute_readme_requests function."""

    def test_execute_readme_requests_groups_by_input(
        self, mock_flake: MagicMock
    ) -> None:
        """Test that execute_readme_requests groups requests by input_name."""
        # Create readme requests from different inputs
        requests: list[ReadmeRequest] = [
            {"input_name": None, "function_name": "wireguard"},
            {"input_name": None, "function_name": "zerotier"},
            {"input_name": "custom-services", "function_name": "my-service"},
        ]

        # Mock get_service_readmes to return different collections per input
        with patch("clan_lib.llm.phases.get_service_readmes") as mock_get_readmes:
            # Setup return values for different inputs
            def get_readmes_side_effect(
                input_name: str | None, _service_names: list[str], _flake: MagicMock
            ) -> ServiceReadmeCollection:
                if input_name is None:
                    return ServiceReadmeCollection(
                        input_name=None,
                        readmes={
                            "wireguard": "# WireGuard README",
                            "zerotier": "# ZeroTier README",
                        },
                    )
                return ServiceReadmeCollection(
                    input_name="custom-services",
                    readmes={"my-service": "# My Service README"},
                )

            mock_get_readmes.side_effect = get_readmes_side_effect

            # Execute the requests
            results = execute_readme_requests(requests, mock_flake)

            # Verify grouping and fetching
            assert len(results) == 2  # Two different input sources
            assert None in results
            assert "custom-services" in results

            # Verify built-in services
            assert results[None].input_name is None
            assert "wireguard" in results[None].readmes
            assert "zerotier" in results[None].readmes

            # Verify custom service
            assert results["custom-services"].input_name == "custom-services"
            assert "my-service" in results["custom-services"].readmes

            # Verify get_service_readmes was called correctly
            assert mock_get_readmes.call_count == 2

    def test_execute_readme_requests_single_input(self, mock_flake: MagicMock) -> None:
        """Test execute_readme_requests with all requests from same input."""
        requests: list[ReadmeRequest] = [
            {"input_name": None, "function_name": "wireguard"},
            {"input_name": None, "function_name": "zerotier"},
            {"input_name": None, "function_name": "mycelium"},
        ]

        with patch("clan_lib.llm.phases.get_service_readmes") as mock_get_readmes:
            mock_get_readmes.return_value = ServiceReadmeCollection(
                input_name=None,
                readmes={
                    "wireguard": "# WireGuard",
                    "zerotier": "# ZeroTier",
                    "mycelium": "# Mycelium",
                },
            )

            results = execute_readme_requests(requests, mock_flake)

            # Should only have one input
            assert len(results) == 1
            assert None in results

            # Verify all services are in the result
            assert len(results[None].readmes) == 3

            # Verify get_service_readmes was called once with all service names
            mock_get_readmes.assert_called_once()
            call_args = mock_get_readmes.call_args
            assert call_args[0][0] is None  # input_name
            assert set(call_args[0][1]) == {"wireguard", "zerotier", "mycelium"}


class TestProcessChatTurnPendingFinalDecision:
    """Test process_chat_turn when resuming from pending_final_decision state."""

    def test_final_message_branch_in_pending_final_decision(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test the if final_message branch at line 425 (resume from pending_final_decision)."""
        # Build conversation history including the question that led to pending state
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {"role": "assistant", "content": trace_data[1]["response"]["message"]},
            {"role": "user", "content": "Hmm zerotier please"},
            {
                "role": "assistant",
                "content": trace_data[3]["response"]["message"],
            },  # Question about controller
        ]

        # Session state with pending_final_decision
        session_state: SessionState = cast(
            "SessionState",
            {
                "pending_final_decision": {
                    "service_name": "zerotier",
                    "service_summary": "ZeroTier is a mesh VPN that provides...",
                }
            },
        )

        # Use trace entry where LLM asks another clarifying question
        # (e.g., asking about moons after user answered about controller)
        clarify_trace = trace_data[4]
        assert clarify_trace["stage"] == "final_decision"
        assert len(clarify_trace["response"]["function_calls"]) == 0
        assert clarify_trace["response"]["message"] != ""

        # Mock the final decision to return another clarifying question
        with (
            patch("clan_lib.llm.phases.aggregate_ollama_function_schemas") as mock_agg,
            patch("clan_lib.llm.phases.call_claude_api") as mock_call,
        ):
            mock_agg.return_value = MagicMock(
                tools=[
                    {
                        "type": "function",
                        "function": {"name": "zerotier", "description": "ZeroTier VPN"},
                    }
                ]
            )

            # Return no function calls but a clarifying message
            response = create_openai_response([], clarify_trace["response"]["message"])
            mock_call.return_value = response

            result = get_llm_turn(
                user_request="gchq-local as controller",
                flake=mock_flake,
                conversation_history=conversation_history,
                provider="claude",
                session_state=session_state,
                execute_next_action=True,  # Execute the pending final decision
            )

            # Verify the if final_message branch was taken
            assert result.requires_user_response is True
            assert result.assistant_message == clarify_trace["response"]["message"]

            # Verify pending_final_decision state is STILL set (not cleared)
            assert "pending_final_decision" in result.session_state
            assert (
                result.session_state["pending_final_decision"]["service_name"]
                == "zerotier"
            )

            # No proposed instances yet
            assert len(result.proposed_instances) == 0

            # Conversation history should have grown
            assert len(result.conversation_history) == len(conversation_history) + 2

    def test_pending_final_decision_completes_with_configuration(
        self, trace_data: list[dict[str, Any]], mock_flake: MagicMock
    ) -> None:
        """Test completing configuration from pending_final_decision state."""
        # Build conversation history
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {"role": "assistant", "content": "Here are the VPNs..."},
            {"role": "user", "content": "Use zerotier"},
            {"role": "assistant", "content": "Which machine as controller?"},
        ]

        # Session state with pending_final_decision
        session_state: SessionState = cast(
            "SessionState",
            {
                "pending_final_decision": {
                    "service_name": "zerotier",
                    "service_summary": "ZeroTier mesh VPN",
                }
            },
        )

        # Use final trace entry with complete configuration
        final_trace = trace_data[-1]
        function_calls = final_trace["response"]["function_calls"]
        assert len(function_calls) == 1

        # Mock to return configuration
        with (
            patch("clan_lib.llm.phases.aggregate_ollama_function_schemas") as mock_agg,
            patch("clan_lib.llm.phases.call_claude_api") as mock_call,
        ):
            mock_agg.return_value = MagicMock(
                tools=[
                    {
                        "type": "function",
                        "function": {"name": "zerotier", "description": "ZeroTier VPN"},
                    }
                ]
            )

            response = create_openai_response(function_calls, "")
            mock_call.return_value = response

            result = get_llm_turn(
                user_request="gchq-local as controller, qube-email as moon, rest as peers",
                flake=mock_flake,
                conversation_history=conversation_history,
                provider="claude",
                session_state=session_state,
                execute_next_action=True,  # Execute the pending final decision
            )

            # Verify configuration completed
            assert result.requires_user_response is False
            assert len(result.proposed_instances) == 1
            assert result.proposed_instances[0]["module"]["name"] == "zerotier"

            # Verify pending_final_decision state is CLEARED
            assert "pending_final_decision" not in result.session_state

            # No error
            assert result.error is None


class TestErrorCases:
    """Test error handling in process_chat_turn."""

    def test_llm_provides_no_readme_requests_and_no_message(
        self, mock_flake: MagicMock
    ) -> None:
        """Test error case when LLM provides neither readme requests nor message."""
        # Create response with no function calls and no message (unexpected)
        response = create_openai_response([], "")

        with (
            patch("clan_lib.llm.phases.call_claude_api", return_value=response),
            pytest.raises(ClanAiError, match="did not provide any response"),
        ):
            # Use multi-turn workflow to execute through discovery
            execute_multi_turn_workflow(
                user_request="Setup a VPN",
                flake=mock_flake,
                provider="claude",
            )

    def test_exception_during_processing(self, mock_flake: MagicMock) -> None:
        """Test exception handling in process_chat_turn."""
        # Mock to raise an exception during discovery
        with (
            patch(
                "clan_lib.llm.orchestrator.get_llm_discovery_phase",
                side_effect=ValueError("Test error"),
            ),
            pytest.raises(ValueError, match="Test error"),
        ):
            # Use multi-turn workflow to execute through discovery
            execute_multi_turn_workflow(
                user_request="Setup a VPN",
                flake=mock_flake,
                provider="claude",
            )

    def test_exception_with_existing_conversation_history(
        self, mock_flake: MagicMock
    ) -> None:
        """Test exception handling with existing conversation history."""
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "What VPNs are available?"},
            {"role": "assistant", "content": "Here are the options..."},
        ]

        with (
            patch(
                "clan_lib.llm.orchestrator.get_llm_discovery_phase",
                side_effect=RuntimeError("Network error"),
            ),
            pytest.raises(RuntimeError, match="Network error"),
        ):
            # Use multi-turn workflow to execute through discovery
            execute_multi_turn_workflow(
                user_request="Setup zerotier",
                flake=mock_flake,
                conversation_history=conversation_history,
                provider="claude",
            )

    def test_service_selection_fails_no_service_selected(
        self, mock_flake: MagicMock
    ) -> None:
        """Test error when service selection returns no service and no clarification."""
        # Setup discovery phase to return READMEs
        discovery_response = create_openai_response(
            [
                {"name": "get_readme", "arguments": {"function_name": "zerotier"}},
            ],
            "",
        )

        with (
            patch(
                "clan_lib.llm.phases.call_claude_api", return_value=discovery_response
            ),
            patch("clan_lib.llm.orchestrator.execute_readme_requests") as mock_execute,
            patch(
                "clan_lib.llm.orchestrator.get_llm_service_selection"
            ) as mock_selection,
            patch("clan_lib.llm.orchestrator.get_llm_final_decision") as mock_final,
        ):
            mock_execute.return_value = {
                None: ServiceReadmeCollection(
                    input_name=None, readmes={"zerotier": "# ZeroTier"}
                )
            }
            # Return invalid selection result (no service, no clarification)
            mock_selection.return_value = ServiceSelectionResult(
                selected_service=None,
                service_summary=None,
                clarifying_message="",
            )
            mock_final.return_value = ([], "")

            # Should raise ClanAiError
            with pytest.raises(ClanAiError, match="Failed to select service"):
                # Use multi-turn workflow to execute through service selection
                execute_multi_turn_workflow(
                    user_request="Setup VPN",
                    flake=mock_flake,
                    provider="claude",
                )


class TestGetLlmServiceSelectionErrors:
    """Test error cases in get_llm_service_selection."""

    def test_multiple_select_service_calls(self) -> None:
        """Test error when LLM returns multiple select_service calls."""
        readme_results: dict[str | None, ServiceReadmeCollection] = {
            None: ServiceReadmeCollection(
                input_name=None, readmes={"zerotier": "# ZeroTier"}
            )
        }

        # Create response with multiple select_service calls
        function_calls = [
            {"name": "select_service", "arguments": {"service_name": "zerotier"}},
            {"name": "select_service", "arguments": {"service_name": "wireguard"}},
        ]
        response = create_openai_response(function_calls, "")

        with patch("clan_lib.llm.phases.call_claude_api", return_value=response):
            result = get_llm_service_selection(
                user_request="Setup VPN",
                readme_results=readme_results,
                provider="claude",
            )

            # Should return error - no service selected
            assert result.selected_service is None
            assert result.service_summary is None
            # Clarifying message should indicate the error
            assert result.clarifying_message != ""

    def test_wrong_function_call_name(self) -> None:
        """Test error when LLM calls wrong function instead of select_service."""
        readme_results: dict[str | None, ServiceReadmeCollection] = {
            None: ServiceReadmeCollection(
                input_name=None, readmes={"zerotier": "# ZeroTier"}
            )
        }

        # Create response with wrong function name
        function_calls = [
            {"name": "configure_service", "arguments": {"service_name": "zerotier"}},
        ]
        response = create_openai_response(function_calls, "")

        with patch("clan_lib.llm.phases.call_claude_api", return_value=response):
            result = get_llm_service_selection(
                user_request="Setup VPN",
                readme_results=readme_results,
                provider="claude",
            )

            # Should return error
            assert result.selected_service is None
            assert result.service_summary is None

    def test_missing_required_fields(self) -> None:
        """Test error when select_service call is missing required fields."""
        readme_results: dict[str | None, ServiceReadmeCollection] = {
            None: ServiceReadmeCollection(
                input_name=None, readmes={"zerotier": "# ZeroTier"}
            )
        }

        # Create response with missing summary field
        function_calls = [
            {
                "name": "select_service",
                "arguments": {"service_name": "zerotier"},  # Missing 'summary'
            },
        ]
        response = create_openai_response(function_calls, "")

        with patch("clan_lib.llm.phases.call_claude_api", return_value=response):
            result = get_llm_service_selection(
                user_request="Setup VPN",
                readme_results=readme_results,
                provider="claude",
            )

            # Should return error
            assert result.selected_service is None
            assert result.service_summary is None

    def test_invalid_json_arguments(self) -> None:
        """Test error when select_service arguments cannot be parsed."""
        readme_results: dict[str | None, ServiceReadmeCollection] = {
            None: ServiceReadmeCollection(
                input_name=None, readmes={"zerotier": "# ZeroTier"}
            )
        }

        # Create a malformed response (manually construct to avoid JSON parsing)
        response = cast(
            "OpenAIChatCompletionResponse",
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_0",
                                    "type": "function",
                                    "function": {
                                        "name": "select_service",
                                        "arguments": "{invalid json}",  # Invalid JSON
                                    },
                                }
                            ],
                        },
                    }
                ],
            },
        )

        with patch("clan_lib.llm.phases.call_claude_api", return_value=response):
            result = get_llm_service_selection(
                user_request="Setup VPN",
                readme_results=readme_results,
                provider="claude",
            )

            # Should handle error gracefully
            assert result.selected_service is None
            assert result.service_summary is None

    def test_no_function_calls_and_no_message(self) -> None:
        """Test error when LLM provides no function calls and no message."""
        readme_results: dict[str | None, ServiceReadmeCollection] = {
            None: ServiceReadmeCollection(
                input_name=None, readmes={"zerotier": "# ZeroTier"}
            )
        }

        # Response with no function calls and no message
        response = create_openai_response([], "")

        with patch("clan_lib.llm.phases.call_claude_api", return_value=response):
            result = get_llm_service_selection(
                user_request="Setup VPN",
                readme_results=readme_results,
                provider="claude",
            )

            # Should return error
            assert result.selected_service is None
            assert result.service_summary is None
            assert result.clarifying_message != ""


class TestGetLlmFinalDecisionErrors:
    """Test error cases in get_llm_final_decision."""

    def test_multiple_tools_for_service(self, mock_flake: MagicMock) -> None:
        """Test error when multiple tools match the selected service."""
        with (
            patch("clan_lib.llm.phases.aggregate_ollama_function_schemas") as mock_agg,
            patch("clan_lib.llm.phases.call_claude_api") as mock_call,
        ):
            # Mock multiple tools with same name (unexpected)
            mock_agg.return_value = MagicMock(
                tools=[
                    {
                        "type": "function",
                        "function": {"name": "zerotier", "description": "ZeroTier 1"},
                    },
                    {
                        "type": "function",
                        "function": {"name": "zerotier", "description": "ZeroTier 2"},
                    },
                ]
            )

            response = create_openai_response([], "test message")
            mock_call.return_value = response

            # Should raise ClanAiError
            with pytest.raises(ClanAiError, match="Expected exactly 1 tool"):
                get_llm_final_decision(
                    user_request="Setup zerotier",
                    flake=mock_flake,
                    selected_service="zerotier",
                    service_summary="ZeroTier VPN",
                    provider="claude",
                )

    def test_pending_final_decision_no_response_error(
        self, mock_flake: MagicMock
    ) -> None:
        """Test error when LLM provides neither function_calls nor message in pending_final_decision."""
        # Build conversation history
        conversation_history: list[ChatMessage] = [
            {"role": "user", "content": "Setup VPN"},
            {"role": "assistant", "content": "Which service?"},
            {"role": "user", "content": "Use zerotier"},
            {"role": "assistant", "content": "Which machine as controller?"},
        ]

        # Session state with pending_final_decision
        session_state: SessionState = cast(
            "SessionState",
            {
                "pending_final_decision": {
                    "service_name": "zerotier",
                    "service_summary": "ZeroTier mesh VPN",
                }
            },
        )

        # Mock to return neither function_calls nor message (unexpected)
        with (
            patch("clan_lib.llm.phases.aggregate_ollama_function_schemas") as mock_agg,
            patch("clan_lib.llm.phases.call_claude_api") as mock_call,
        ):
            mock_agg.return_value = MagicMock(
                tools=[
                    {
                        "type": "function",
                        "function": {"name": "zerotier", "description": "ZeroTier VPN"},
                    }
                ]
            )
            # Empty response - no function calls, no message
            response = create_openai_response([], "")
            mock_call.return_value = response

            # Should raise ClanAiError
            with pytest.raises(ClanAiError, match="LLM did not provide any response"):
                # Use multi-turn workflow to execute through final decision
                execute_multi_turn_workflow(
                    user_request="gchq-local as controller",
                    flake=mock_flake,
                    conversation_history=conversation_history,
                    provider="claude",
                    session_state=session_state,
                )


class TestParseOpenaiResponse:
    """Test parse_openai_response function from endpoints.py."""

    def test_parse_with_function_calls_and_content(self) -> None:
        """Test parsing response with both function calls and text content."""
        response = cast(
            "OpenAIChatCompletionResponse",
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Here is my response",
                            "tool_calls": [
                                {
                                    "id": "call_123",
                                    "type": "function",
                                    "function": {
                                        "name": "test_function",
                                        "arguments": '{"arg1": "value1"}',
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
        )

        function_calls, message = parse_openai_response(response)

        assert len(function_calls) == 1
        assert function_calls[0]["name"] == "test_function"
        assert function_calls[0]["arguments"] == '{"arg1": "value1"}'
        assert function_calls[0]["id"] == "call_123"
        assert function_calls[0]["type"] == "function_call"
        assert message == "Here is my response"

    def test_parse_with_no_choices(self) -> None:
        """Test parsing response with no choices."""
        response = cast("OpenAIChatCompletionResponse", {"choices": []})

        function_calls, message = parse_openai_response(response)

        assert len(function_calls) == 0
        assert message == ""

    def test_parse_with_missing_choices_key(self) -> None:
        """Test parsing response with missing choices key."""
        response = cast("OpenAIChatCompletionResponse", {})

        function_calls, message = parse_openai_response(response)

        assert len(function_calls) == 0
        assert message == ""

    def test_parse_with_no_tool_calls(self) -> None:
        """Test parsing response with content but no tool calls."""
        response = cast(
            "OpenAIChatCompletionResponse",
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Just a text response",
                        }
                    }
                ]
            },
        )

        function_calls, message = parse_openai_response(response)

        assert len(function_calls) == 0
        assert message == "Just a text response"

    def test_parse_with_tool_calls_but_no_content(self) -> None:
        """Test parsing response with tool calls but empty content."""
        response = cast(
            "OpenAIChatCompletionResponse",
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "",
                            "tool_calls": [
                                {
                                    "id": "call_456",
                                    "type": "function",
                                    "function": {
                                        "name": "configure_service",
                                        "arguments": '{"service": "zerotier"}',
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
        )

        function_calls, message = parse_openai_response(response)

        assert len(function_calls) == 1
        assert function_calls[0]["name"] == "configure_service"
        assert message == ""

    def test_parse_with_multiple_tool_calls(self) -> None:
        """Test parsing response with multiple function calls."""
        response = cast(
            "OpenAIChatCompletionResponse",
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Calling multiple functions",
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "function": {
                                        "name": "func1",
                                        "arguments": "{}",
                                    },
                                },
                                {
                                    "id": "call_2",
                                    "function": {
                                        "name": "func2",
                                        "arguments": '{"key": "value"}',
                                    },
                                },
                            ],
                        }
                    }
                ]
            },
        )

        function_calls, message = parse_openai_response(response)

        assert len(function_calls) == 2
        assert function_calls[0]["name"] == "func1"
        assert function_calls[1]["name"] == "func2"
        assert message == "Calling multiple functions"


class TestParseOllamaResponse:
    """Test parse_ollama_response function from endpoints.py."""

    def test_parse_with_function_calls_and_content(self) -> None:
        """Test parsing Ollama response with both function calls and content."""
        response = cast(
            "OllamaChatResponse",
            {
                "message": {
                    "role": "assistant",
                    "content": "Here is my response",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "test_function",
                                "arguments": {"arg1": "value1"},
                            }
                        }
                    ],
                }
            },
        )

        function_calls, message = parse_ollama_response(response)

        assert len(function_calls) == 1
        assert function_calls[0]["name"] == "test_function"
        # Ollama response has dict arguments that get JSON stringified
        args = json.loads(function_calls[0]["arguments"])
        assert args == {"arg1": "value1"}
        assert function_calls[0]["type"] == "function_call"
        assert message == "Here is my response"

    def test_parse_with_no_message(self) -> None:
        """Test parsing Ollama response with no message."""
        response = cast("OllamaChatResponse", {})

        function_calls, message = parse_ollama_response(response)

        assert len(function_calls) == 0
        assert message == ""

    def test_parse_with_no_tool_calls(self) -> None:
        """Test parsing Ollama response with content but no tool calls."""
        response = cast(
            "OllamaChatResponse",
            {
                "message": {
                    "role": "assistant",
                    "content": "Just a text response",
                }
            },
        )

        function_calls, message = parse_ollama_response(response)

        assert len(function_calls) == 0
        assert message == "Just a text response"

    def test_parse_with_tool_calls_but_no_content(self) -> None:
        """Test parsing Ollama response with tool calls but empty content."""
        response = cast(
            "OllamaChatResponse",
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "configure_service",
                                "arguments": {"service": "zerotier"},
                            }
                        }
                    ],
                }
            },
        )

        function_calls, message = parse_ollama_response(response)

        assert len(function_calls) == 1
        assert function_calls[0]["name"] == "configure_service"
        assert message == ""

    def test_parse_with_multiple_tool_calls(self) -> None:
        """Test parsing Ollama response with multiple function calls."""
        response = cast(
            "OllamaChatResponse",
            {
                "message": {
                    "role": "assistant",
                    "content": "Calling multiple functions",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "func1",
                                "arguments": {},
                            }
                        },
                        {
                            "function": {
                                "name": "func2",
                                "arguments": {"key": "value"},
                            }
                        },
                    ],
                }
            },
        )

        function_calls, message = parse_ollama_response(response)

        assert len(function_calls) == 2
        assert function_calls[0]["name"] == "func1"
        assert function_calls[1]["name"] == "func2"
        assert message == "Calling multiple functions"
