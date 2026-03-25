#!/usr/bin/env python3
"""Format nix code blocks inside markdown files using nixfmt.

Used as a treefmt formatter. Requires nixfmt on PATH.
"""

import re
import subprocess
import sys
from pathlib import Path


def format_nix(code: str) -> str:
    """Run nixfmt on a code string, return original on failure."""
    try:
        result = subprocess.run(
            ["nixfmt"],
            input=code,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return code


def process_file(path: str) -> bool:
    """Process a markdown file, returns True if changes were made."""
    p = Path(path)
    content = p.read_text()

    def replace_block(m: re.Match) -> str:
        fence_open = m.group(1)
        code = m.group(2)
        formatted = format_nix(code)
        return f"{fence_open}\n{formatted}```"

    new_content = re.sub(
        r"(```nix)\n(.*?)```",
        replace_block,
        content,
        flags=re.DOTALL,
    )

    if new_content != content:
        p.write_text(new_content)
    return new_content != content


if __name__ == "__main__":
    for path in sys.argv[1:]:
        process_file(path)
