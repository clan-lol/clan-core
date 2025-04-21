from clan_cli.cmd import run
from clan_cli.nix import nix_shell

_works: bool | None = None


def bubblewrap_works() -> bool:
    global _works
    if _works is None:
        _works = _bubblewrap_works()
    return _works


def _bubblewrap_works() -> bool:
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
            "bash", "-c", ":"
        ],
    )
    # fmt: on
    try:
        run(cmd)
    except Exception:
        return False
    else:
        return True
