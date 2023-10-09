import asyncio
import logging
import shlex
from pathlib import Path
from typing import Optional, Tuple

from .errors import ClanError

log = logging.getLogger(__name__)


async def run(cmd: list[str], cwd: Optional[Path] = None) -> Tuple[bytes, bytes]:
    log.debug(f"$: {shlex.join(cmd)}")
    cwd_res = None
    if cwd is not None:
        if not cwd.exists():
            raise ClanError(f"Working directory {cwd} does not exist")
        if not cwd.is_dir():
            raise ClanError(f"Working directory {cwd} is not a directory")
        cwd_res = cwd.resolve()
        log.debug(f"Working directory: {cwd_res}")
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
exit code: {proc.returncode}
command output:
{stderr.decode("utf-8")}
"""
        )
    return stdout, stderr
