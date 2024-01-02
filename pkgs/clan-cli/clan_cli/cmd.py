import logging
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

from .errors import ClanError

log = logging.getLogger(__name__)


class CmdOut(NamedTuple):
    stdout: str
    stderr: str
    cwd: Path | None = None


def run(cmd: list[str], cwd: Path = Path.cwd()) -> CmdOut:
    # Start the subprocess
    process = subprocess.Popen(
        cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Initialize empty strings for output and error
    output = b""
    error = b""

    # Iterate over the stdout stream
    for c in iter(lambda: process.stdout.read(1), b""):  # type: ignore
        # Convert bytes to string and append to output
        output += c
        # Write to terminal
        sys.stdout.buffer.write(c)
    # Iterate over the stderr stream
    for c in iter(lambda: process.stderr.read(1), b""):  # type: ignore
        # Convert bytes to string and append to error
        error += c
        # Write to terminal
        sys.stderr.buffer.write(c)
    # Wait for the subprocess to finish
    process.wait()

    output_str = output.decode("utf-8")
    error_str = error.decode("utf-8")

    if process.returncode != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
working directory: {cwd}
exit code: {process.returncode}
stderr:
{error_str}
stdout:
{output_str}
"""
        )
    return CmdOut(output_str, error_str, cwd=cwd)


def runforcli(func: Callable[..., dict[str, CmdOut]], *args: Any) -> None:
    try:
        res = func(*args)

        for name, out in res.items():
            if out.stderr:
                print(f"{name}: {out.stderr}", end="")
            if out.stdout:
                print(f"{name}: {out.stdout}", end="")
    except ClanError as e:
        print(e)
        exit(1)
