"""Nix store setup utilities for VM tests"""

import ctypes
import errno
import os
import subprocess
from functools import cache
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

# These paths will be substituted during package build
CP_BIN = "@cp@"
NIX_STORE_BIN = "@nix-store@"
XARGS_BIN = "@xargs@"
MOUNT_BIN = "@mount@"


# Load the C library
libc = ctypes.CDLL("libc.so.6", use_errno=True)

# Define the mount function
libc.mount.argtypes = [
    ctypes.c_char_p,  # source
    ctypes.c_char_p,  # target
    ctypes.c_char_p,  # filesystemtype
    ctypes.c_ulong,  # mountflags
    ctypes.c_void_p,  # data
]
libc.mount.restype = ctypes.c_int

MS_BIND = 0x1000

# Number of colon-separated fields in an /etc/group line:
# group-name:password:gid:user-list
GROUP_FILE_FIELDS = 4


def mount(
    source: Path,
    target: Path,
    filesystemtype: str,
    mountflags: int = 0,
    data: str | None = None,
) -> None:
    """A Python wrapper for the mount system call.

    :param source: The source of the file system (e.g., device name, remote filesystem).
    :param target: The mount point (an existing directory).
    :param filesystemtype: The filesystem type (e.g., "ext4", "nfs").
    :param mountflags: Mount options flags.
    :param data: File system-specific data (e.g., options like "rw").
    :raises OSError: If the mount system call fails.
    """
    # Convert Python strings to C-compatible strings
    source_c = ctypes.c_char_p(str(source).encode("utf-8"))
    target_c = ctypes.c_char_p(str(target).encode("utf-8"))
    fstype_c = ctypes.c_char_p(filesystemtype.encode("utf-8"))
    data_c = ctypes.c_char_p(data.encode("utf-8")) if data else None

    # Call the mount system call
    result = libc.mount(
        source_c,
        target_c,
        fstype_c,
        ctypes.c_ulong(mountflags),
        data_c,
    )

    if result != 0:
        err = ctypes.get_errno()
        raise OSError(err, os.strerror(err))


@cache
def fixup_passwd_group() -> None:
    """Bind-mount minimal /etc/passwd and /etc/group with a real nixbld user and group.

    Nix build sandboxes ship a /etc/passwd where both root and nixbld map to uid 0,
    and a /etc/group where nixbld has no members. Nix (and clan-cli) refuse to work
    in that state with "the build users group 'nixbld' has no members". The old
    custom container-test-driver patched this up; upstream nspawn does not.

    Skipped when /etc/group already lists at least one nixbld member (e.g. the
    QEMU test-driver host, whose nix build sandbox provides a usable nixbld).
    If the bind mount fails (EPERM inside a nix sandbox without CAP_SYS_ADMIN),
    leave the existing databases in place -- the caller's nix invocation will
    surface the real problem with a clear error if the fixup was actually needed.
    """
    try:
        group_contents = Path("/etc/group").read_text()
    except OSError:
        group_contents = ""
    for line in group_contents.splitlines():
        parts = line.split(":")
        if (
            len(parts) >= GROUP_FILE_FIELDS
            and parts[0] == "nixbld"
            and parts[3].strip()
        ):
            return

    user_db_lines = (
        "root:x:0:0:Root:/root:/bin/sh\n"
        "nixbld:x:1000:100:Nix build user:/tmp:/bin/sh\n"
        "nobody:x:65534:65534:Nobody:/:/bin/sh\n"
    )
    group_db_lines = "root:x:0:\nnixbld:x:100:nixbld\nnogroup:x:65534:\n"

    with NamedTemporaryFile(mode="w", delete=False, prefix="test-passwd-") as f:
        f.write(user_db_lines)
        passwd_path = f.name
    with NamedTemporaryFile(mode="w", delete=False, prefix="test-group-") as f:
        f.write(group_db_lines)
        group_path = f.name

    try:
        mount(
            source=Path(passwd_path),
            target=Path("/etc/passwd"),
            filesystemtype="",
            mountflags=MS_BIND,
            data=None,
        )
        mount(
            source=Path(group_path),
            target=Path("/etc/group"),
            filesystemtype="",
            mountflags=MS_BIND,
            data=None,
        )
    except OSError as exc:
        if exc.errno == errno.EPERM:
            return
        raise


def setup_nix_in_nix(
    closure_info: str | None,
) -> Path:
    """Set up Nix store inside test environment

    Args:
        closure_info: Path to closure info directory containing store-paths file,
            or None if no closure info
    """
    # Ensure /etc/passwd and /etc/group have a real nixbld user/group so nix works
    fixup_passwd_group()

    # Remove NIX_REMOTE if present (we don't have any nix daemon running)
    if "NIX_REMOTE" in os.environ:
        del os.environ["NIX_REMOTE"]

    # Set NIX_CONFIG globally to disable substituters for speed
    os.environ["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "

    temp_dir = str(TemporaryDirectory(delete=False).name)

    # Set up environment variables for test environment
    os.environ["HOME"] = str(temp_dir)
    os.environ["NIX_STATE_DIR"] = f"{temp_dir}/nix"
    os.environ["NIX_CONF_DIR"] = f"{temp_dir}/etc"
    os.environ["IN_NIX_SANDBOX"] = "1"
    os.environ["CLAN_TEST_STORE"] = f"{temp_dir}/store"
    os.environ["LOCK_NIX"] = f"{temp_dir}/nix_lock"

    # Create necessary directories
    Path(f"{temp_dir}/nix").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/etc").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/store").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/store/nix/store").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/store/nix/var/nix/gcroots").mkdir(parents=True, exist_ok=True)

    # Set up Nix store if closure info is provided
    if closure_info and Path(closure_info).exists():
        store_paths_file = Path(closure_info) / "store-paths"
        if store_paths_file.exists():
            # Use bind mounts when running as root (uid 0), otherwise copy
            use_bind_mount = os.getuid() == 0
            if use_bind_mount:
                for path in store_paths_file.read_text().splitlines():
                    if not path.strip():
                        continue
                    target = Path(f"{temp_dir}/store/nix/store/{Path(path).name}")
                    if Path(path).is_dir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.touch()
                    mount(
                        source=Path(path),
                        target=target,
                        filesystemtype="",
                        mountflags=MS_BIND,
                        data=None,
                    )
            else:
                # Use xargs with parallel processing to copy store paths efficiently
                # --reflink=auto enables copy-on-write when filesystem supports it
                num_cpus = str(min(4, os.cpu_count() or 1))
                with store_paths_file.open() as f:
                    subprocess.run(
                        [
                            XARGS_BIN,
                            "-r",
                            f"-P{num_cpus}",
                            CP_BIN,
                            "--no-dereference",
                            "--recursive",
                            "--reflink=auto",  # Use copy-on-write if available
                            "--target-directory",
                            f"{temp_dir}/store/nix/store",
                        ],
                        stdin=f,
                        check=True,
                    )

            # Load Nix database
            registration_file = Path(closure_info) / "registration"
            if registration_file.exists():
                with registration_file.open() as f:
                    subprocess.run(
                        [NIX_STORE_BIN, "--load-db", "--store", f"{temp_dir}/store"],
                        input=f.read(),
                        text=True,
                        check=True,
                    )
    return Path(f"{temp_dir}/store")


def prepare_test_flake(
    temp_dir: str,
    clan_core_for_checks: str,
    closure_info: str,
) -> tuple[Path, Path]:
    """Set up Nix store and copy test flake to temporary directory

    Args:
        temp_dir: Temporary directory
        clan_core_for_checks: Path to clan-core-for-checks
        closure_info: Path to closure info for Nix store setup

    Returns:
        Path to the test flake directory
    """
    # Set up Nix store
    store_dir = setup_nix_in_nix(closure_info)

    # Copy test flake
    flake_dir = Path(temp_dir) / "test-flake"
    subprocess.run(["cp", "-r", clan_core_for_checks, flake_dir], check=True)
    subprocess.run(["chmod", "-R", "+w", flake_dir], check=True)
    return flake_dir, store_dir
