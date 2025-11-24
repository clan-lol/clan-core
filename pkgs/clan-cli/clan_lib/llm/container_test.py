import contextlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import clan_lib.llm.llm_types
import pytest
from clan_lib.flake.flake import Flake
from clan_lib.llm.llm_types import ModelConfig
from clan_lib.llm.orchestrator import get_llm_turn
from clan_lib.llm.service import create_llm_model, run_llm_service
from clan_lib.service_runner import create_service_manager

if TYPE_CHECKING:
    from clan_lib.llm.llm_types import ChatResult
    from clan_lib.llm.schemas import SessionState


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


@pytest.mark.service_runner
@pytest.mark.usefixtures("mock_nix_shell", "llm_service")
def test_full_conversation_flow(mock_flake: MagicMock) -> None:
    """Test the complete conversation flow by manually calling get_llm_turn at each step.

    This test verifies:
    - State transitions through discovery -> readme_fetch -> service_selection -> final_decision
    - Each step returns the correct next_action
    - Conversation history is preserved across turns
    - Session state is correctly maintained
    """
    flake = mock_flake
    trace_file = Path("~/.ollama/container_test_llm_trace.json").expanduser()
    trace_file.unlink(missing_ok=True)  # Start fresh
    provider = "ollama"

    # Override DEFAULT_MODELS with 4-minute timeouts for container tests
    clan_lib.llm.llm_types.DEFAULT_MODELS = {
        "ollama": ModelConfig(
            name="qwen3:4b-instruct",
            provider="ollama",
            timeout=None,  # set inference timeout to 5 minutes as CI may be slow
            temperature=0,  # set randomness to 0 for consistent test results
        ),
    }

    # ========== STEP 1: Initial request (should return next_action for discovery) ==========
    print_separator("STEP 1: Initial Request", char="=", width=80)
    result = get_llm_turn(
        user_request="What VPN options do I have?",
        flake=flake,
        provider=provider,  # type: ignore[arg-type]
        execute_next_action=False,
        trace_file=trace_file,
    )

    # Should have next_action for discovery phase
    assert result.next_action is not None, "Should have next_action for discovery"
    assert result.next_action["type"] == "discovery"
    assert result.requires_user_response is False
    assert len(result.proposed_instances) == 0
    assert "pending_discovery" in result.session_state
    print(f"  Next Action: {result.next_action['type']}")
    print(f"  Description: {result.next_action['description']}")
    print_meta_info(result, turn=1, phase="Initial Request")

    # ========== STEP 2: Execute discovery (should return next_action for readme_fetch) ==========
    print_separator("STEP 2: Execute Discovery", char="=", width=80)
    result = get_llm_turn(
        user_request="",
        flake=flake,
        conversation_history=list(result.conversation_history),
        provider=provider,  # type: ignore[arg-type]
        session_state=result.session_state,
        execute_next_action=True,
        trace_file=trace_file,
    )

    # Should have next_action for readme fetch OR a clarifying question
    if result.next_action:
        assert result.next_action["type"] == "fetch_readmes"
        assert "pending_readme_fetch" in result.session_state
        print(f"  Next Action: {result.next_action['type']}")
        print(f"  Description: {result.next_action['description']}")
    else:
        # LLM asked a clarifying question
        assert result.requires_user_response is True
        assert len(result.assistant_message) > 0
        print(f"  Assistant Message: {result.assistant_message[:100]}...")
    print_meta_info(result, turn=2, phase="Discovery Executed")

    # ========== STEP 3: Execute readme fetch (if applicable) ==========
    if result.next_action and result.next_action["type"] == "fetch_readmes":
        print_separator("STEP 3: Execute Readme Fetch", char="=", width=80)
        result = get_llm_turn(
            user_request="",
            flake=flake,
            conversation_history=list(result.conversation_history),
            provider=provider,  # type: ignore[arg-type]
            session_state=result.session_state,
            execute_next_action=True,
            trace_file=trace_file,
        )

        # Should have next_action for service selection
        assert result.next_action is not None
        assert result.next_action["type"] == "service_selection"
        assert "pending_service_selection" in result.session_state
        print(f"  Next Action: {result.next_action['type']}")
        print(f"  Description: {result.next_action['description']}")
        print_meta_info(result, turn=3, phase="Readme Fetch Executed")

        # ========== STEP 4: Execute service selection ==========
        print_separator("STEP 4: Execute Service Selection", char="=", width=80)
        result = get_llm_turn(
            user_request="I want ZeroTier.",
            flake=flake,
            conversation_history=list(result.conversation_history),
            provider=provider,  # type: ignore[arg-type]
            session_state=result.session_state,
            execute_next_action=True,
            trace_file=trace_file,
        )

        # Should either have next_action for final_decision OR a clarifying question
        if result.next_action:
            assert result.next_action["type"] == "final_decision"
            assert "pending_final_decision" in result.session_state
            print(f"  Next Action: {result.next_action['type']}")
            print(f"  Description: {result.next_action['description']}")
        else:
            # LLM asked a clarifying question during service selection
            assert result.requires_user_response is True
            assert len(result.assistant_message) > 0
            print(f"  Assistant Message: {result.assistant_message[:100]}...")
        print_meta_info(result, turn=4, phase="Service Selection Executed")

        # ========== STEP 5: Execute final decision (if applicable) ==========
        if result.next_action and result.next_action["type"] == "final_decision":
            print_separator("STEP 5: Execute Final Decision", char="=", width=80)
            result = get_llm_turn(
                user_request="",
                flake=flake,
                conversation_history=list(result.conversation_history),
                provider=provider,  # type: ignore[arg-type]
                session_state=result.session_state,
                execute_next_action=True,
                trace_file=trace_file,
            )

            # Should either have proposed_instances OR ask a clarifying question
            if result.proposed_instances:
                assert len(result.proposed_instances) > 0
                assert result.next_action is None
                print(f"  Proposed Instances: {len(result.proposed_instances)}")
                for inst in result.proposed_instances:
                    print(f"    - {inst['module']['name']}")
            else:
                # LLM asked a clarifying question
                assert result.requires_user_response is True
                assert len(result.assistant_message) > 0
                print(f"  Assistant Message: {result.assistant_message[:100]}...")
            print_meta_info(result, turn=5, phase="Final Decision Executed")

    # Verify conversation history has grown
    assert len(result.conversation_history) > 0
    assert result.conversation_history[0]["content"] == "What VPN options do I have?"
