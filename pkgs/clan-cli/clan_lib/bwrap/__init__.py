import os
import shutil
from functools import cache
from pathlib import Path

from clan_lib.cmd import Log, RunOpts, run
from clan_lib.nix import nix_shell


@cache
def bubblewrap_works() -> bool:
    real_bash_path = Path("bash")
    if os.environ.get("IN_NIX_SANDBOX"):
        bash_executable_path = Path(str(shutil.which("bash")))
        real_bash_path = bash_executable_path.resolve()

    # fmt: off
    cmd = nix_shell(
        [
            "bash",
            "bubblewrap",
        ],
        [
            "bwrap",
            "--unshare-all",
            "--tmpfs",  "/",
            "--ro-bind", "/nix/store", "/nix/store",
            "--dev", "/dev",
            "--chdir", "/",
            "--bind", "/proc", "/proc",
            "--uid", "1000",
            "--gid", "1000",
            "--",
            # do nothing, just test if bash executes
            str(real_bash_path), "-c", ":",
        ],
    )

    # fmt: on
    res = run(cmd, RunOpts(log=Log.BOTH, check=False))
    return res.returncode == 0
