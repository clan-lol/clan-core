import asyncio
import logging
import shlex

from .errors import ClanError

log = logging.getLogger(__name__)


async def run(cmd: list[str]) -> bytes:
    log.debug(f"$: {shlex.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
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
    return stdout
