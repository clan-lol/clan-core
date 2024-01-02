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
    output = ""
    error = ""

    # Iterate over the stdout stream
    for c in iter(lambda: process.stdout.read(1), b""):  # type: ignore
        # Convert bytes to string and append to output
        output += c.decode("utf-8")
        # Write to terminal
        sys.stdout.write(c.decode("utf-8"))

    # Iterate over the stderr stream
    for c in iter(lambda: process.stderr.read(1), b""):  # type: ignore
        # Convert bytes to string and append to error
        error += c.decode("utf-8")
        # Write to terminal
        sys.stderr.write(c.decode("utf-8"))
    # Wait for the subprocess to finish
    process.wait()

    if process.returncode != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
working directory: {cwd}
exit code: {process.returncode}
stderr:
{error}
stdout:
{output}
"""
        )
    return CmdOut(output, error, cwd=cwd)


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
