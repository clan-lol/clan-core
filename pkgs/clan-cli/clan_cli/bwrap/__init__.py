import os
import shutil
from pathlib import Path

from clan_lib.nix import nix_shell

from clan_cli.cmd import Log, RunOpts, run

_works: bool | None = None


def bubblewrap_works() -> bool:
    global _works
    if _works is None:
        _works = _bubblewrap_works()
    return _works


def _bubblewrap_works() -> bool:
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
            str(real_bash_path), "-c", ":"
        ],
    )

    # fmt: on
    res = run(cmd, RunOpts(log=Log.BOTH, check=False))
    return res.returncode == 0
