import contextlib
import os
import shutil
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from tempfile import NamedTemporaryFile

from clan_lib.nix import nix_shell, nix_test_store


def create_sandbox_profile(
    *,
    ro_paths: list[str] | None = None,
    rw_paths: list[str] | None = None,
) -> str:
    """Create a sandbox profile that allows access to nix store and specified paths.

    Based on Nix's sandbox-defaults.sb implementation.

    Args:
        ro_paths: Paths to allow read-only access to.
        rw_paths: Paths to allow full read-write and process-exec access to.

    """
    rw_rules = ""
    for path in rw_paths or []:
        rw_rules += f'\n(allow file* process-exec network-outbound network-inbound (subpath "{path}"))'

    ro_rules = ""
    for path in ro_paths or []:
        ro_rules += f'\n(allow file-read* (subpath "{path}"))'

    return f"""(version 1)

(deny default)

; Disallow creating setuid/setgid binaries, since that
; would allow breaking build user isolation.
(deny file-write-setugid)

; Allow forking.
(allow process-fork)

; Allow reading system information like #CPUs, etc.
(allow sysctl-read)

; Allow POSIX semaphores and shared memory.
(allow ipc-posix*)

; Allow SYSV semaphores and shared memory.
(allow ipc-sysv*)

; Allow socket creation.
(allow system-socket)

; Allow sending signals within the sandbox.
(allow signal (target same-sandbox))

; Allow getpwuid.
(allow mach-lookup (global-name "com.apple.system.opendirectoryd.libinfo"))

; Allow read access to the Nix store
(allow file-read* (subpath "/nix/store"))

; Allow access to macOS temporary directories structure (both symlink and real paths)
(allow file-read* file-write* file-write-create file-write-unlink (subpath "/var/folders"))
(allow file-read* file-write* file-write-create file-write-unlink (subpath "/private/var/folders"))
(allow file-read* file-write* file-write-create file-write-unlink (subpath "/tmp"))
(allow file-read* file-write* file-write-create file-write-unlink (subpath "/private/tmp"))

; Allow reading directory structure for getcwd
(allow file-read-metadata (subpath "/"))
(allow file-read-metadata (subpath "/private"))

; Some packages like to read the system version.
(allow file-read*
 (literal "/System/Library/CoreServices/SystemVersion.plist")
 (literal "/System/Library/CoreServices/SystemVersionCompat.plist"))

; Without this line clang cannot write to /dev/null, breaking some configure tests.
(allow file-read-metadata (literal "/dev"))

; Allow read and write access to /dev/null
(allow file-read* file-write* (literal "/dev/null"))
(allow file-read* (literal "/dev/random"))
(allow file-read* (literal "/dev/urandom"))

; Allow local networking (localhost only)
(allow network* (remote ip "localhost:*"))
(allow network-inbound (local ip "*:*"))

; Allow access to /etc/resolv.conf for DNS resolution
(allow file-read* (literal "/etc/resolv.conf"))
(allow file-read* (literal "/private/etc/resolv.conf"))

; Allow reading from common system paths that scripts might need
(allow file-read* (literal "/"))
(allow file-read* (literal "/usr"))
(allow file-read* (literal "/bin"))
(allow file-read* (literal "/sbin"))

; Allow execution of binaries from Nix store and system paths
(allow process-exec (subpath "/nix/store"))
(allow process-exec (literal "/bin/bash"))
(allow process-exec (literal "/bin/sh"))
(allow process-exec (literal "/usr/bin/env"))

; Additional read-write paths{rw_rules}

; Additional read-only paths{ro_rules}
"""


@contextmanager
def sandbox_exec_cmd(
    cmd: list[str],
    *,
    ro_paths: list[str] | None = None,
    rw_paths: list[str] | None = None,
) -> Iterator[list[str]]:
    """Run a command inside a macOS sandbox-exec sandbox.

    Args:
        cmd: The command to run inside the sandbox.
        ro_paths: Paths to allow read-only access to.
        rw_paths: Paths to allow full read-write access to.
            Paths are resolved to handle macOS symlinks
            (e.g. /var/folders -> /private/var/folders).

    Yields:
        The full command list.

    """
    # Resolve paths to handle macOS symlinks (/var/folders -> /private/var/folders)
    resolved_rw = [str(Path(p).resolve()) for p in (rw_paths or [])]
    resolved_ro = [str(Path(p).resolve()) for p in (ro_paths or [])]

    profile_content = create_sandbox_profile(ro_paths=resolved_ro, rw_paths=resolved_rw)

    with NamedTemporaryFile(mode="w", suffix=".sb", delete=False) as f:
        f.write(profile_content)
        profile_path = f.name

    try:
        yield [
            "/usr/bin/sandbox-exec",
            "-f",
            profile_path,
            *cmd,
        ]
    finally:
        with contextlib.suppress(OSError):
            Path(profile_path).unlink()


@cache
def sandbox_bash() -> str:
    """Resolve bash for use inside a sandbox, handling nix build environments."""
    if os.environ.get("IN_NIX_SANDBOX"):
        bash_path = shutil.which("bash")
        if bash_path:
            return str(Path(bash_path).resolve())
    return "bash"


def bubblewrap_cmd(
    cmd: list[str],
    *,
    ro_binds: list[tuple[str, str]] | None = None,
    rw_binds: list[tuple[str, str]] | None = None,
) -> list[str]:
    """Run a command inside a bubblewrap sandbox.

    Args:
        cmd: The command to run inside the sandbox.
        ro_binds: Additional read-only bind mounts as (src, dest) pairs.
        rw_binds: Additional read-write bind mounts as (src, dest) pairs.

    Returns:
        The full command list, provided via nix_shell.

    """
    test_store = nix_test_store()

    extra_args: list[str] = []
    for src, dest in ro_binds or []:
        extra_args += ["--ro-bind", src, dest]
    for src, dest in rw_binds or []:
        extra_args += ["--bind", src, dest]

    sandbox_tmp = Path("/tmp")  # noqa: S108 -- bwrap mount target, not host tmpdir

    # fmt: off
    return nix_shell(
        ["bash", "bubblewrap"],
        [
            "bwrap",
            "--unshare-all",
            "--tmpfs",  "/",
            "--ro-bind", "/nix/store", "/nix/store",
            "--ro-bind", "/bin/sh", "/bin/sh",
            *(["--ro-bind", str(test_store), str(test_store)] if test_store else []),
            "--dev", "/dev",
            "--bind", "/proc", "/proc",
            "--tmpfs", str(sandbox_tmp),
            "--chdir", "/",
            "--uid", "1000",
            "--gid", "1000",
            *extra_args,
            "--",
            *cmd,
        ],
    )
    # fmt: on


@cache
def sandbox_works() -> bool:
    """Check if sandboxing is available on the current platform."""
    if sys.platform == "linux":
        from clan_lib.bwrap import bubblewrap_works  # noqa: PLC0415

        return bubblewrap_works()
    if sys.platform == "darwin":
        return Path("/usr/bin/sandbox-exec").exists()
    return False


@contextmanager
def sandbox_cmd(
    cmd: list[str],
    *,
    ro_paths: list[str] | None = None,
    rw_paths: list[str] | None = None,
) -> Iterator[list[str]]:
    """Run a command in a platform-appropriate sandbox.

    On Linux, uses bubblewrap. On macOS, uses sandbox-exec.

    Args:
        cmd: The command to run inside the sandbox.
        ro_paths: Paths to allow read-only access to.
        rw_paths: Paths to allow read-write access to.

    Yields:
        The full command list.

    Raises:
        NotImplementedError: If the current platform has no sandbox backend.

    """
    if sys.platform == "linux":
        ro_binds = [(p, p) for p in (ro_paths or [])]
        rw_binds = [(p, p) for p in (rw_paths or [])]
        yield bubblewrap_cmd(cmd, ro_binds=ro_binds, rw_binds=rw_binds)
    elif sys.platform == "darwin":
        with sandbox_exec_cmd(cmd, ro_paths=ro_paths, rw_paths=rw_paths) as result:
            yield result
    else:
        msg = f"Sandboxing is not supported on {sys.platform}"
        raise NotImplementedError(msg)
