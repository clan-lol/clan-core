import contextlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest
from clan_lib.flake.flake import Flake
from clan_lib.llm.orchestrator import get_llm_turn
from clan_lib.llm.service import create_llm_model, run_llm_service
from clan_lib.service_runner import create_service_manager

if TYPE_CHECKING:
    from clan_lib.llm.llm_types import ChatResult
    from clan_lib.llm.schemas import ChatMessage, SessionState


def get_current_mode(session_state: "SessionState") -> str:
    """Extract the current mode from session state."""
    if "pending_service_selection" in session_state:
        return "SERVICE_SELECTION"
    if "pending_final_decision" in session_state:
        return "FINAL_DECISION"
    return "DISCOVERY"


def print_separator(
    title: str = "", char: str = "=", width: int = 80, double: bool = True
) -> None:
    """Print a separator line with optional title."""
    if double:
        print(f"\n{char * width}")
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"{char * padding} {title} {char * padding}")
    if double or title:
        print(f"{char * width}")


def print_meta_info(result: "ChatResult", turn: int, phase: str) -> None:
    """Print meta information section in a structured format."""
    mode = get_current_mode(result.session_state)
    print_separator("META INFORMATION", char="-", width=80, double=False)
    print(f"  Turn Number:           {turn}")
    print(f"  Phase:                 {phase}")
    print(f"  Current Mode:          {mode}")
    print(f"  Requires User Input:   {result.requires_user_response}")
    print(f"  Conversation Length:   {len(result.conversation_history)} messages")
    print(f"  Proposed Instances:    {len(result.proposed_instances)}")
    print(f"  Has Next Action:       {result.next_action is not None}")
    print(f"  Session State Keys:    {list(result.session_state.keys())}")
    if result.error:
        print(f"  Error:                 {result.error}")
    print("-" * 80)


def print_chat_exchange(
    user_msg: str | None, assistant_msg: str, session_state: "SessionState"
) -> None:
    """Print a chat exchange with role labels and current mode."""
    mode = get_current_mode(session_state)
    print_separator("CHAT EXCHANGE", char="-", width=80, double=False)

    if user_msg:
        print("\n  USER:")
        print(f"  {user_msg}")

    print(f"\n  ASSISTANT [{mode}]:")
    # Wrap long messages
    max_line_length = 76
    words = assistant_msg.split()
    current_line = "  "
    for word in words:
        if len(current_line) + len(word) + 1 > max_line_length:
            print(current_line)
            current_line = "  " + word
        else:
            current_line += (" " if len(current_line) > 2 else "") + word
    if current_line.strip():
        print(current_line)

    print("\n" + "-" * 80)


@pytest.fixture
def mock_flake() -> MagicMock:
    """Create a mock Flake object with test data."""
    flake_mock = MagicMock(spec=Flake)
    test_data_dir = Path(__file__).parent / "container_data"

    def load_json(filename: str) -> dict | list:
        """Load and parse a JSON file from container_data directory."""
        return json.loads((test_data_dir / filename).read_text())

    # Configure flake.select to return values based on the argument
    def select_side_effect(arg: str) -> dict | list:
        # Handle staticModules readme requests dynamically
        if arg.startswith(
            "clanInternals.inventoryClass.staticModules.{"
        ) and arg.endswith("}.manifest.readme"):
            # Extract service names from the pattern: {service1,service2,...}
            services_part = arg.split("{")[1].split("}")[0]
            requested_services = [s.strip() for s in services_part.split(",")]

            # Load all VPN readmes (always returns a dict for this file)
            all_readmes = load_json("vpns_readme.json")
            assert isinstance(all_readmes, dict), (
                "vpns_readme.json should contain a dict"
            )

            # Return only the requested services
            return {
                svc: all_readmes[svc]
                for svc in requested_services
                if svc in all_readmes
            }

        match arg:
            case "clanInternals.inventoryClass.inventorySerialization.{instances,machines,meta}":
                return load_json("inventory_instances_machines_meta.json")
            case "clanInternals.inventoryClass.inventorySerialization.{tags}":
                return load_json("inventory_tags.json")
            case "clanInternals.inventoryClass.modulesPerSource":
                return load_json("modules_per_source.json")
            case "clanInternals.inventoryClass.staticModules":
                return load_json("static_modules.json")
            case _:
                msg = f"Unexpected flake.select argument: {arg}"
                raise ValueError(msg)

    flake_mock.select.side_effect = select_side_effect
    return flake_mock


@pytest.fixture
def mock_nix_shell() -> Iterator[MagicMock]:
    """Patch nix_shell function with test data."""

    # Configure nix_shell to return values based on the arguments
    def nix_shell_side_effect(packages: list[str], cmd: list[str]) -> list[str]:
        match (tuple(packages), tuple(cmd)):
            case (("ollama",), ("ollama", "pull", _)):
                return ["ollama", "list"]
            case (("ollama",), _):
                return cmd
            case _:
                msg = f"Unexpected nix_shell arguments: packages={packages}, cmd={cmd}"
                raise ValueError(msg)

    with patch("clan_lib.llm.service.nix_shell") as mock:
        mock.side_effect = nix_shell_side_effect
        yield mock


@pytest.fixture
def llm_service() -> Iterator[None]:
    """Start LLM service and create model, ensuring cleanup."""
    service_manager = create_service_manager()

    try:
        run_llm_service()
        create_llm_model()
        yield
    finally:
        # Always attempt to stop the service, even if setup failed
        with contextlib.suppress(Exception):
            service_manager.stop_service("ollama")


def execute_multi_turn_workflow(
    user_request: str,
    flake: Flake | MagicMock,
    conversation_history: list["ChatMessage"] | None = None,
    provider: str = "ollama",
    session_state: "SessionState | None" = None,
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


@pytest.mark.service_runner
@pytest.mark.usefixtures("mock_nix_shell", "llm_service")
def test_full_conversation_flow(mock_flake: MagicMock) -> None:
    """Comprehensive test that exercises the complete conversation flow with the actual LLM service.

    This test simulates a realistic multi-turn conversation that covers:
    - Discovery phase: Initial request and LLM gathering information
    - Service selection phase: User choosing from available options
    - Final decision phase: Configuring the selected service with specific parameters
    - State transitions: pending_service_selection -> pending_final_decision -> completion
    - Conversation history preservation across all turns
    - Error handling and edge cases
    """
    flake = mock_flake
    # ========== TURN 1: Discovery Phase - Initial vague request ==========
    print_separator("TURN 1: Discovery Phase", char="=", width=80)
    result = execute_multi_turn_workflow(
        user_request="What VPN options do I have?",
        flake=flake,
        provider="ollama",
    )

    # Verify discovery phase behavior
    assert result.requires_user_response is True, (
        "Should require user response in discovery"
    )
    assert len(result.conversation_history) >= 2, (
        "Should have user + assistant messages"
    )
    assert result.conversation_history[0]["role"] == "user"
    assert result.conversation_history[0]["content"] == "What VPN options do I have?"
    assert result.conversation_history[-1]["role"] == "assistant"
    assert len(result.assistant_message) > 0, "Assistant should provide a response"

    # After multi-turn execution, we may have either:
    # - pending_service_selection (if LLM provided options and is waiting for choice)
    # - pending_final_decision (if LLM directly selected a service)
    # - no pending state (if LLM asked a clarifying question)

    # No instances yet
    assert len(result.proposed_instances) == 0
    assert result.error is None

    print_chat_exchange(
        "What VPN options do I have?", result.assistant_message, result.session_state
    )
    print_meta_info(result, turn=1, phase="Discovery")

    # ========== TURN 2: Service Selection Phase - User makes a choice ==========
    print_separator("TURN 2: Service Selection", char="=", width=80)
    user_msg_2 = "I'll use ZeroTier please"
    result = execute_multi_turn_workflow(
        user_request=user_msg_2,
        flake=flake,
        conversation_history=list(result.conversation_history),
        provider="ollama",
        session_state=result.session_state,
    )

    # Verify conversation history growth and preservation
    assert len(result.conversation_history) > 2, "History should grow"
    assert result.conversation_history[0]["content"] == "What VPN options do I have?"
    assert result.conversation_history[2]["content"] == "I'll use ZeroTier please"

    # Should either ask for configuration details or provide direct config
    # Most likely will ask for more details (pending_final_decision)
    if result.requires_user_response:
        # LLM is asking for configuration details
        assert len(result.assistant_message) > 0
        # Should transition to final decision phase
        if "pending_final_decision" not in result.session_state:
            # Might still be in service selection asking clarifications
            assert "pending_service_selection" in result.session_state
    else:
        # LLM provided configuration immediately (less likely)
        assert len(result.proposed_instances) > 0
        assert result.proposed_instances[0]["module"]["name"] == "zerotier"

    print_chat_exchange(user_msg_2, result.assistant_message, result.session_state)
    print_meta_info(result, turn=2, phase="Service Selection")

    # ========== Continue conversation until we reach final decision or completion ==========
    max_turns = 10
    turn_count = 2

    while result.requires_user_response and turn_count < max_turns:
        turn_count += 1

        # Determine appropriate response based on current state
        if "pending_service_selection" in result.session_state:
            # Still selecting service
            user_request = "Yes, ZeroTier"
            phase = "Service Selection (continued)"
        elif "pending_final_decision" in result.session_state:
            # Configuring the service
            user_request = "Set up gchq-local as controller, qube-email as moon, and wintux as peer"
            phase = "Final Configuration"
        else:
            # Generic continuation
            user_request = "Yes, that sounds good. Use gchq-local as controller."
            phase = "Continuing Conversation"

        print_separator(f"TURN {turn_count}: {phase}", char="=", width=80)

        result = execute_multi_turn_workflow(
            user_request=user_request,
            flake=flake,
            conversation_history=list(result.conversation_history),
            provider="ollama",
            session_state=result.session_state,
        )

        # Verify conversation history continues to grow
        assert len(result.conversation_history) == (turn_count * 2), (
            f"History should have {turn_count * 2} messages (turn {turn_count})"
        )

        # Verify history preservation
        assert (
            result.conversation_history[0]["content"] == "What VPN options do I have?"
        )

        print_chat_exchange(
            user_request, result.assistant_message, result.session_state
        )
        print_meta_info(result, turn=turn_count, phase=phase)

        # Check for completion
        if not result.requires_user_response:
            print_separator("CONVERSATION COMPLETED", char="=", width=80)
            break

    # ========== Final Verification ==========
    print_separator("FINAL VERIFICATION", char="=", width=80)
    assert turn_count < max_turns, f"Conversation took too many turns ({turn_count})"

    # If conversation completed, verify we have valid configuration
    if not result.requires_user_response:
        assert len(result.proposed_instances) > 0, (
            "Should have at least one proposed instance"
        )
        instance = result.proposed_instances[0]

        # Verify instance structure
        assert "module" in instance
        assert "name" in instance["module"]
        assert instance["module"]["name"] in [
            "zerotier",
            "wireguard",
            "yggdrasil",
            "mycelium",
        ]

        # Should not be in pending state anymore
        assert "pending_service_selection" not in result.session_state
        assert "pending_final_decision" not in result.session_state

        assert result.error is None, f"Should not have error: {result.error}"

        print_separator("FINAL SUMMARY", char="-", width=80, double=False)
        print("  Status:                SUCCESS")
        print(f"  Module Name:           {instance['module']['name']}")
        print(f"  Total Turns:           {turn_count}")
        print(f"  Final History Length:  {len(result.conversation_history)} messages")
        if "roles" in instance:
            roles_list = ", ".join(instance["roles"].keys())
            print(f"  Configuration Roles:   {roles_list}")
        print("  Errors:                None")
        print("-" * 80)
    else:
        # Conversation didn't complete but should have made progress
        assert len(result.conversation_history) > 2
        assert result.error is None
        print_separator("FINAL SUMMARY", char="-", width=80, double=False)
        print("  Status:                IN PROGRESS")
        print(f"  Total Turns:           {turn_count}")
        print(f"  Current State:         {list(result.session_state.keys())}")
        print(f"  History Length:        {len(result.conversation_history)} messages")
        print("-" * 80)
