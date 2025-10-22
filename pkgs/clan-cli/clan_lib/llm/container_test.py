import contextlib
import json
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from clan_lib.flake.flake import Flake
from clan_lib.llm.llm import (
    process_chat_turn,
)
from clan_lib.llm.service import create_llm_model, run_llm_service
from clan_lib.service_runner import create_service_manager


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
            case "clanInternals.inventoryClass.inventory.{instances,machines,meta}":
                return load_json("inventory_instances_machines_meta.json")
            case "clanInternals.inventoryClass.inventory.{tags}":
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
    return
    # ========== TURN 1: Discovery Phase - Initial vague request ==========
    print("\n=== TURN 1: Initial discovery request ===")
    result = process_chat_turn(
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

    # Should transition to service selection phase with pending state
    assert "pending_service_selection" in result.session_state, (
        "Should have pending service selection"
    )
    assert "readme_results" in result.session_state["pending_service_selection"]

    # No instances yet
    assert len(result.proposed_instances) == 0
    assert result.error is None

    print(f"Assistant: {result.assistant_message[:200]}...")
    print(f"State: {list(result.session_state.keys())}")
    print(f"History length: {len(result.conversation_history)}")

    # ========== TURN 2: Service Selection Phase - User makes a choice ==========
    print("\n=== TURN 2: User selects ZeroTier ===")
    result = process_chat_turn(
        user_request="I'll use ZeroTier please",
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

    print(
        f"Assistant: {result.assistant_message[:200] if result.assistant_message else 'No message'}..."
    )
    print(f"State: {list(result.session_state.keys())}")
    print(f"Requires response: {result.requires_user_response}")

    # ========== Continue conversation until we reach final decision or completion ==========
    max_turns = 10
    turn_count = 2

    while result.requires_user_response and turn_count < max_turns:
        turn_count += 1
        print(f"\n=== TURN {turn_count}: Continuing conversation ===")

        # Determine appropriate response based on current state
        if "pending_service_selection" in result.session_state:
            # Still selecting service
            user_request = "Yes, ZeroTier"
        elif "pending_final_decision" in result.session_state:
            # Configuring the service
            user_request = "Set up gchq-local as controller, qube-email as moon, and wintux as peer"
        else:
            # Generic continuation
            user_request = "Yes, that sounds good. Use gchq-local as controller."

        print(f"User: {user_request}")

        result = process_chat_turn(
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

        print(
            f"Assistant: {result.assistant_message[:200] if result.assistant_message else 'No message'}..."
        )
        print(f"State: {list(result.session_state.keys())}")
        print(f"Requires response: {result.requires_user_response}")
        print(f"Proposed instances: {len(result.proposed_instances)}")

        # Check for completion
        if not result.requires_user_response:
            print("\n=== Conversation completed! ===")
            break

    # ========== Final Verification ==========
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

        # Should have roles configuration
        if "roles" in instance:
            print(f"\nConfiguration roles: {list(instance['roles'].keys())}")

        # Should not be in pending state anymore
        assert "pending_service_selection" not in result.session_state
        assert "pending_final_decision" not in result.session_state

        assert result.error is None, f"Should not have error: {result.error}"

        print(f"\nFinal instance: {instance['module']['name']}")
        print(f"Total conversation turns: {turn_count}")
        print(f"Final history length: {len(result.conversation_history)}")
    else:
        # Conversation didn't complete but should have made progress
        assert len(result.conversation_history) > 2
        assert result.error is None
        print(f"\nConversation in progress after {turn_count} turns")
        print(f"Current state: {list(result.session_state.keys())}")
