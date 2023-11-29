import logging
import multiprocessing as mp
import os
import shlex
import stat
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import ipdb

log = logging.getLogger(__name__)


def command_exec(cmd: list[str], work_dir: Path, env: dict[str, str]) -> None:
    subprocess.run(cmd, check=True, env=env, cwd=work_dir.resolve())


def block_for_input() -> None:
    log = logging.getLogger(__name__)
    procid = os.getpid()
    f"echo 'continue' > /sys/proc/{procid}/fd/{sys.stdin.fileno()}"

    while True:
        log.warning("Use sudo cntr attach <pid> to attach to the container.")
        # log.warning("Resume execution by executing '%s' in cntr shell", command)
        time.sleep(1)
    log.info("Resuming execution.")


def breakpoint_container(
    work_dir: Path,
    env: dict[str, str] | None = None,
    cmd: list[str] | None = None,
) -> None:
    if env is None:
        env = os.environ.copy()
    else:
        env = env.copy()

    dump_env(env, work_dir / "env.sh")

    if cmd is not None:
        log.debug("Command: %s", shlex.join(cmd))
        mycommand = shlex.join(cmd)
        write_command(mycommand, work_dir / "cmd.sh")

    block_for_input()


def breakpoint_shell(
    work_dir: Path = Path(os.getcwd()),
    env: dict[str, str] | None = None,
    cmd: list[str] | None = None,
) -> None:
    if env is None:
        env = os.environ.copy()
    else:
        env = env.copy()

    # Cmd appending
    args = ["xterm", "-e", "zsh", "-df"]
    if cmd is not None:
        mycommand = shlex.join(cmd)
        write_command(mycommand, work_dir / "cmd.sh")
    proc = spawn_process(func=command_exec, cmd=args, work_dir=work_dir, env=env)

    try:
        ipdb.set_trace()
    finally:
        proc.terminate()


def write_command(command: str, loc: Path) -> None:
    log.info("Dumping command to %s", loc)
    with open(loc, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(command)
    st = os.stat(loc)
    os.chmod(loc, st.st_mode | stat.S_IEXEC)


def spawn_process(func: Callable, **kwargs: Any) -> mp.Process:
    if mp.get_start_method(allow_none=True) is None:
        mp.set_start_method(method="spawn")

    proc = mp.Process(target=func, name="python-debug-process", kwargs=kwargs)
    proc.start()
    return proc


def dump_env(env: dict[str, str], loc: Path) -> None:
    cenv = env.copy()
    log.info("Dumping environment variables to %s", loc)
    with open(loc, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        for k, v in cenv.items():
            if v.count("\n") > 0 or v.count('"') > 0 or v.count("'") > 0:
                continue
            f.write(f"export {k}='{v}'\n")
    st = os.stat(loc)
    os.chmod(loc, st.st_mode | stat.S_IEXEC)
