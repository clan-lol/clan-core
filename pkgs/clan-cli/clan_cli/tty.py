import sys
from collections.abc import Callable
from typing import IO, Any


def is_interactive() -> bool:
    """Returns true if the current process is interactive"""
    return sys.stdin.isatty() and sys.stdout.isatty()


def color_text(code: int, file: IO[Any] = sys.stdout) -> Callable[[str], None]:
    """
    Print with color if stderr is a tty
    """

    def wrapper(text: str) -> None:
        if file.isatty():
            print(f"\x1b[{code}m{text}\x1b[0m", file=file)
        else:
            print(text, file=file)

    return wrapper


warn = color_text(91, file=sys.stderr)
info = color_text(92, file=sys.stderr)
