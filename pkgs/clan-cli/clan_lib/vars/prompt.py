import enum
import logging
import sys
import termios
import tty
from dataclasses import dataclass, field
from typing import Any, TypedDict

from clan_lib.errors import ClanError

log = logging.getLogger(__name__)

# This is for simulating user input in tests.
MOCK_PROMPT_RESPONSE: None = None

# ASCII control character constants
CTRL_D_ASCII = 4  # EOF character
CTRL_C_ASCII = 3  # Interrupt character
DEL_ASCII = 127  # Delete character
BACKSPACE_ASCII = 8  # Backspace character


class PromptType(enum.Enum):
    LINE = "line"
    HIDDEN = "hidden"
    MULTILINE = "multiline"
    MULTILINE_HIDDEN = "multiline-hidden"


class Display(TypedDict):
    label: str | None
    group: str | None
    helperText: str | None
    required: bool


@dataclass
class Prompt:
    name: str
    description: str
    prompt_type: PromptType

    persist: bool = False
    previous_value: str | None = None
    display: Display = field(
        default_factory=lambda: Display(
            {
                "label": None,
                "group": None,
                "helperText": None,
                "required": False,
            },
        ),
    )

    @classmethod
    def from_nix(cls: type["Prompt"], data: dict[str, Any]) -> "Prompt":
        return cls(
            name=data["name"],
            description=data.get("description", data["name"]),
            prompt_type=PromptType(data.get("type", "line")),
            persist=data.get("persist", False),
            display=data.get("display", {}),
        )


HIDDEN_PREVIOUS_VALUE_MARKER = "<Enter to keep, Backspace for new>"


def get_input(multiline: bool, hidden: bool, previous_value: str | None = None) -> str:
    """Get input from the user using raw terminal mode.

    Args:
        multiline: If True, allows multiple lines with Ctrl-D to finish.
                   If False, reads a single line, finishing on Enter.
        hidden: If True, input is not echoed to the terminal.
                If False, input is visible as typed.
        previous_value: If provided, pre-fills the input (non-hidden) or shows
                        a marker that can be accepted with Enter (hidden).

    """
    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    lines: list[str] = []
    current_line: list[str] = []

    # Track whether we're showing the "keep previous" marker for hidden input
    showing_previous_marker = False

    # Handle previous value pre-fill
    if previous_value is not None:
        if hidden:
            # For hidden input, show a marker that user can accept or clear
            sys.stdout.write(HIDDEN_PREVIOUS_VALUE_MARKER)
            sys.stdout.flush()
            showing_previous_marker = True
        # For non-hidden input, pre-fill and display the previous value
        elif multiline:
            prev_lines = previous_value.split("\n")
            if prev_lines:
                current_line = list(prev_lines[-1])
                lines = prev_lines[:-1]
                sys.stdout.write(previous_value)
                sys.stdout.flush()
        else:
            current_line = list(previous_value)
            sys.stdout.write(previous_value)
            sys.stdout.flush()

    try:
        # Change terminal settings - use raw mode
        tty.setraw(fd)

        while True:
            char = sys.stdin.read(1)

            # Check for Ctrl-C (KeyboardInterrupt)
            if ord(char) == CTRL_C_ASCII:
                raise KeyboardInterrupt

            # Handle the "keep previous value" marker for hidden input
            if showing_previous_marker:
                # Clear the marker from display
                sys.stdout.write("\b \b" * len(HIDDEN_PREVIOUS_VALUE_MARKER))
                sys.stdout.flush()

                # Enter or Ctrl-D: keep previous value
                if char in {"\r", "\n"} or not char or ord(char) == CTRL_D_ASCII:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                    print()
                    return previous_value  # type: ignore[return-value]

                # Any other key: clear marker and continue with normal input
                showing_previous_marker = False
                # If it's not backspace, treat it as the first character of new input
                if ord(char) not in {DEL_ASCII, BACKSPACE_ASCII}:
                    current_line.append(char)
                continue

            # Check for Ctrl-D (ASCII value 4 or EOF)
            if not char or ord(char) == CTRL_D_ASCII:
                # Add last line if not empty
                if current_line:
                    lines.append("".join(current_line))
                break

            # Handle Enter key
            if char in {"\r", "\n"}:
                if not multiline:
                    # Single line mode: finish on Enter
                    lines.append("".join(current_line))
                    break
                lines.append("".join(current_line))
                current_line = []
                # Print newline for visual feedback
                sys.stdout.write("\r\n")
                sys.stdout.flush()
            # Handle backspace
            elif ord(char) == DEL_ASCII or ord(char) == BACKSPACE_ASCII:
                if current_line:
                    current_line.pop()
                    # Erase character on screen if not hidden
                    if not hidden:
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
            # Regular character
            else:
                current_line.append(char)
                # Echo character if not hidden
                if not hidden:
                    sys.stdout.write(char)
                    sys.stdout.flush()

    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        # Print a final newline for clean display
        print()

    return "\n".join(lines)


def _get_secret_input_with_confirmation(
    ident: str,
    input_type: PromptType,
    text: str,
    previous_value: str | None = None,
    max_attempts: int = 3,
) -> str:
    """Get secret input with confirmation, retrying on mismatch.

    If a previous_value is provided and the user presses Enter to keep it,
    confirmation is skipped since the value isn't changing.
    """
    for attempt in range(max_attempts):
        try:
            # Get first input
            match input_type:
                case PromptType.MULTILINE_HIDDEN:
                    print(
                        "Enter multiple lines "
                        "(press Ctrl-D to finish or Ctrl-C to cancel):"
                    )
                    first_input = get_input(
                        multiline=True, hidden=True, previous_value=previous_value
                    )
                case PromptType.HIDDEN:
                    print(f"{text} (hidden): ", end="", flush=True)
                    first_input = get_input(
                        multiline=False, hidden=True, previous_value=previous_value
                    )
                case _:
                    msg = f"Unsupported input type: {input_type}"
                    raise ClanError(msg)

            # Skip confirmation if user kept previous value
            if previous_value is not None and first_input == previous_value:
                log.info("Kept previous value. Processing...")
                return first_input

            # Get confirmation input
            match input_type:
                case PromptType.MULTILINE_HIDDEN:
                    print(
                        "Confirm by entering the same value again "
                        "(press Ctrl-D to finish or Ctrl-C to cancel):"
                    )
                    second_input = get_input(multiline=True, hidden=True)
                case PromptType.HIDDEN:
                    print(f"Confirm {text} (hidden): ", end="", flush=True)
                    second_input = get_input(multiline=False, hidden=True)
                case _:
                    msg = f"Unsupported input type: {input_type}"
                    raise ClanError(msg)

            if first_input == second_input:
                log.info("Input received and confirmed. Processing...")
                return first_input

            remaining = max_attempts - attempt - 1
            if remaining > 0:
                attempts_text = "attempt" if remaining == 1 else "attempts"
                print(
                    f"Values do not match. {remaining} {attempts_text} remaining.",
                    file=sys.stderr,
                )
            else:
                msg = (
                    f"Failed to confirm value for {ident} "
                    f"after {max_attempts} attempts."
                )
                raise ClanError(msg)

        except (KeyboardInterrupt, EOFError) as e:
            msg = "User cancelled the input."
            raise ClanError(msg) from e

    # Should never reach here due to logic above, but keeping for safety
    msg = f"Failed to get input for {ident}"
    raise ClanError(msg)


def ask(
    ident: str,
    input_type: PromptType,
    label: str | None,
    machine_names: list[str],
    previous_value: str | None = None,
) -> str:
    """Ask user for input, with confirmation for secret inputs."""
    text = label or f"Enter the value for {ident}:"

    log.info(f"Prompting value for {ident} for machines: {', '.join(machine_names)}")

    if MOCK_PROMPT_RESPONSE:
        return next(MOCK_PROMPT_RESPONSE)

    # Secret prompts require confirmation
    if input_type in (PromptType.HIDDEN, PromptType.MULTILINE_HIDDEN):
        return _get_secret_input_with_confirmation(
            ident, input_type, text, previous_value
        )

    # Regular prompts don't need confirmation
    try:
        match input_type:
            case PromptType.LINE:
                print(f"{text}: ", end="", flush=True)
                result = get_input(
                    multiline=False, hidden=False, previous_value=previous_value
                )
            case PromptType.MULTILINE:
                print(f"{text} (Finish with Ctrl-D): ")
                result = get_input(
                    multiline=True, hidden=False, previous_value=previous_value
                )
            case _:
                msg = f"Unsupported input type: {input_type}"
                raise ClanError(msg)
    except (KeyboardInterrupt, EOFError) as e:
        msg = "User cancelled the input."
        raise ClanError(msg) from e

    log.info("Input received. Processing...")
    return result
