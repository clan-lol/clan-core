import logging
import multiprocessing as mp
import os
import shlex
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import ipdb

log = logging.getLogger(__name__)


def command_exec(cmd: List[str], work_dir: Path, env: Dict[str, str]) -> None:
    subprocess.run(cmd, check=True, env=env, cwd=work_dir.resolve())


def repro_env_break(
    work_dir: Path,
    env: Optional[Dict[str, str]] = None,
    cmd: Optional[List[str]] = None,
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
        print(f"Adding to zsh history the command: {mycommand}", file=sys.stderr)
    proc = spawn_process(func=command_exec, cmd=args, work_dir=work_dir, env=env)

    try:
        ipdb.set_trace()
    finally:
        proc.terminate()


def write_command(command: str, loc: Path) -> None:
    with open(loc, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(command)
    st = os.stat(loc)
    os.chmod(loc, st.st_mode | stat.S_IEXEC)


def spawn_process(func: Callable, **kwargs: Any) -> mp.Process:
    if mp.get_start_method(allow_none=True) is None:
        mp.set_start_method(method="spawn")

    proc = mp.Process(target=func, kwargs=kwargs)
    proc.start()
    return proc


def dump_env(env: Dict[str, str], loc: Path) -> None:
    cenv = env.copy()
    with open(loc, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        for k, v in cenv.items():
            if v.count("\n") > 0 or v.count('"') > 0 or v.count("'") > 0:
                continue
            f.write(f"export {k}='{v}'\n")
    st = os.stat(loc)
    os.chmod(loc, st.st_mode | stat.S_IEXEC)
