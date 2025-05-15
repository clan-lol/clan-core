import enum
import logging
import sys
import termios
import tty
from dataclasses import dataclass
from getpass import getpass
from typing import Any

from clan_cli.errors import ClanError

log = logging.getLogger(__name__)

# This is for simulating user input in tests.
MOCK_PROMPT_RESPONSE: None = None


class PromptType(enum.Enum):
    LINE = "line"
    HIDDEN = "hidden"
    MULTILINE = "multiline"
    MULTILINE_HIDDEN = "multiline-hidden"


@dataclass
class Prompt:
    name: str
    description: str
    prompt_type: PromptType

    persist: bool = False
    previous_value: str | None = None

    @classmethod
    def from_json(cls: type["Prompt"], data: dict[str, Any]) -> "Prompt":
        return cls(
            name=data["name"],
            description=data["description"],
            prompt_type=PromptType(data["type"]),
            persist=data.get("persist", data["persist"]),
        )


def get_multiline_hidden_input() -> str:
    """
    Get multiline input from the user without echoing the input.
    This function allows the user to enter multiple lines of text,
    and it will return the concatenated string of all lines entered.
    The user can finish the input by pressing Ctrl-D (EOF).
    """

    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    lines = []
    current_line: list[str] = []

    try:
        # Change terminal settings - disable echo
        tty.setraw(fd)

        while True:
            char = sys.stdin.read(1)

            # Check for Ctrl-D (ASCII value 4 or EOF)
            if not char or ord(char) == 4:
                # Add last line if not empty
                if current_line:
                    lines.append("".join(current_line))
                break

            # Check for Ctrl-C (KeyboardInterrupt)
            if ord(char) == 3:
                raise KeyboardInterrupt

            # Handle Enter key
            if char == "\r" or char == "\n":
                lines.append("".join(current_line))
                current_line = []
                # Print newline for visual feedback
                sys.stdout.write("\r\n")
                sys.stdout.flush()
            # Handle backspace
            elif ord(char) == 127 or ord(char) == 8:
                if current_line:
                    current_line.pop()
            # Regular character
            else:
                current_line.append(char)

    finally:
        # Restore terminal settings
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        # Print a final newline for clean display
        print()

    return "\n".join(lines)


def ask(
    ident: str,
    input_type: PromptType,
    label: str | None,
) -> str:
    text = f"Enter the value for {ident}:"
    if label:
        text = f"{label}"
    log.info(f"Prompting value for {ident}")
    if MOCK_PROMPT_RESPONSE:
        return next(MOCK_PROMPT_RESPONSE)
    try:
        match input_type:
            case PromptType.LINE:
                result = input(f"{text}: ")
            case PromptType.MULTILINE:
                print(f"{text} (Finish with Ctrl-D): ")
                result = sys.stdin.read()
            case PromptType.MULTILINE_HIDDEN:
                print(
                    "Enter multiple lines (press Ctrl-D to finish or Ctrl-C to cancel):"
                )
                result = get_multiline_hidden_input()
            case PromptType.HIDDEN:
                result = getpass(f"{text} (hidden): ")
    except KeyboardInterrupt as e:
        msg = "User cancelled the input."
        raise ClanError(msg) from e

    log.info("Input received. Processing...")
    return result
