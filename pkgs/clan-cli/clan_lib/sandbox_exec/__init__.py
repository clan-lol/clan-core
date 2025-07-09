import contextlib
import os
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile


def create_sandbox_profile() -> str:
    """Create a sandbox profile that allows access to tmpdir and nix store, based on Nix's sandbox-defaults.sb."""

    # Based on Nix's sandbox-defaults.sb implementation with TMPDIR parameter
    profile_content = """(version 1)

(define TMPDIR (param "_TMPDIR"))

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

; Allow full access to our temporary directory and its real path
(allow file* process-exec network-outbound network-inbound
 (subpath TMPDIR))

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
"""

    return profile_content


@contextmanager
def sandbox_exec_cmd(generator: str, tmpdir: Path) -> Iterator[list[str]]:
    """Create a sandbox-exec command for running a generator.

    Yields:
        list[str]: The command to execute
    """
    profile_content = create_sandbox_profile()

    # Create a temporary file for the sandbox profile
    with NamedTemporaryFile(mode="w", suffix=".sb", delete=False) as f:
        f.write(profile_content)
        profile_path = f.name

    try:
        real_bash_path = Path("bash")
        if os.environ.get("IN_NIX_SANDBOX"):
            bash_executable_path = Path(str(shutil.which("bash")))
            real_bash_path = bash_executable_path.resolve()

        # Use the sandbox profile parameter to define TMPDIR and execute from within it
        # Resolve the tmpdir to handle macOS symlinks (/var/folders -> /private/var/folders)
        resolved_tmpdir = tmpdir.resolve()
        cmd = [
            "/usr/bin/sandbox-exec",
            "-f",
            profile_path,
            "-D",
            f"_TMPDIR={resolved_tmpdir}",
            str(real_bash_path),
            "-c",
            generator,
        ]

        yield cmd
    finally:
        # Clean up the profile file
        with contextlib.suppress(OSError):
            Path(profile_path).unlink()
