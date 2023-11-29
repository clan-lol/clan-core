import asyncio
import logging
import shlex
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any, NamedTuple

from .custom_logger import get_caller
from .errors import ClanError

log = logging.getLogger(__name__)


class CmdOut(NamedTuple):
    stdout: str
    stderr: str
    cwd: Path | None = None


async def run(cmd: list[str], cwd: Path | None = None) -> CmdOut:
    cwd_res = None
    if cwd is not None:
        if not cwd.exists():
            raise ClanError(f"Working directory {cwd} does not exist")
        if not cwd.is_dir():
            raise ClanError(f"Working directory {cwd} is not a directory")
        cwd_res = cwd.resolve()
    log.debug(
        f"Command: {shlex.join(cmd)}\nWorking directory: {cwd_res}\nCaller : {get_caller()}"
    )
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd_res,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
working directory: {cwd_res}
exit code: {proc.returncode}
stderr:
{stderr.decode("utf-8")}
stdout:
{stdout.decode("utf-8")}
"""
        )

    return CmdOut(stdout.decode("utf-8"), stderr.decode("utf-8"), cwd=cwd)


def runforcli(
    func: Callable[..., Coroutine[Any, Any, dict[str, CmdOut]]], *args: Any
) -> None:
    try:
        res = asyncio.run(func(*args))

        for name, out in res.items():
            if out.stderr:
                print(f"{name}: {out.stderr}", end="")
            if out.stdout:
                print(f"{name}: {out.stdout}", end="")
    except ClanError as e:
        print(e)
        exit(1)
