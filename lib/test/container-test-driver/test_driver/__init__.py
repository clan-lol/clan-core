"""Test driver for container-based NixOS testing."""

import argparse
import ctypes
import os
import re
import shlex
import shutil
import subprocess
import time
import types
import uuid
from collections.abc import Callable
from contextlib import _GeneratorContextManager
from dataclasses import dataclass
from functools import cache, cached_property
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any

from colorama import Fore, Style

from .logger import AbstractLogger, CompositeLogger, TerminalLogger


@cache
def init_test_environment() -> None:
    """Set up the test environment (network bridge, /etc/passwd) once."""
    # Set up network bridge
    subprocess.run(
        ["ip", "link", "add", "br0", "type", "bridge"],
        check=True,
        text=True,
    )
    subprocess.run(["ip", "link", "set", "br0", "up"], check=True, text=True)
    subprocess.run(
        ["ip", "addr", "add", "192.168.1.254/24", "dev", "br0"],
        check=True,
        text=True,
    )

    # Set up minimal passwd file for unprivileged operations
    # Using Nix's convention: UID 1000 for nixbld user, GID 100 for nixbld group
    passwd_content = """root:x:0:0:Root:/root:/bin/sh
nixbld:x:1000:100:Nix build user:/tmp:/bin/sh
nobody:x:65534:65534:Nobody:/:/bin/sh
"""  # noqa: S105 - This is not a password, it's a Unix passwd file format for testing

    with NamedTemporaryFile(mode="w", delete=False, prefix="test-passwd-") as f:
        f.write(passwd_content)
        passwd_path = f.name

    # Set up minimal group file
    group_content = """root:x:0:
nixbld:x:100:nixbld
nogroup:x:65534:
"""

    with NamedTemporaryFile(mode="w", delete=False, prefix="test-group-") as f:
        f.write(group_content)
        group_path = f.name

    # Bind mount our passwd over the system's /etc/passwd
    result = libc.mount(
        ctypes.c_char_p(passwd_path.encode()),
        ctypes.c_char_p(b"/etc/passwd"),
        ctypes.c_char_p(b"none"),
        ctypes.c_ulong(MS_BIND),
        None,
    )
    if result != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno), "Failed to mount passwd")

    # Bind mount our group over the system's /etc/group
    result = libc.mount(
        ctypes.c_char_p(group_path.encode()),
        ctypes.c_char_p(b"/etc/group"),
        ctypes.c_char_p(b"none"),
        ctypes.c_ulong(MS_BIND),
        None,
    )
    if result != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno), "Failed to mount group")


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
MS_REC = 0x4000


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
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))


class Error(Exception):
    pass


def prepare_machine_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    root.joinpath("etc").mkdir(parents=True, exist_ok=True)
    root.joinpath(".env").write_text(
        "\n".join(f"{k}={v}" for k, v in os.environ.items()),
    )


def pythonize_name(name: str) -> str:
    return re.sub(r"^[^A-z_]|[^A-z0-9_]", "_", name)


def retry(fn: Callable, timeout: int = 900) -> None:
    """Call the given function repeatedly, with 1 second intervals,
    until it returns True or a timeout is reached.
    """
    for _ in range(timeout):
        if fn(False):
            return
        time.sleep(1)

    if not fn(True):
        msg = f"action timed out after {timeout} seconds"
        raise Error(msg)


class Machine:
    def __init__(
        self,
        name: str,
        toplevel: Path,
        logger: AbstractLogger,
        rootdir: Path,
        out_dir: str,
    ) -> None:
        self.name = name
        self.toplevel = toplevel
        self.out_dir = out_dir
        self.process: subprocess.Popen | None = None
        self.rootdir: Path = rootdir
        self.logger = logger

    @cached_property
    def container_pid(self) -> int:
        return self.get_systemd_process()

    def start(self) -> None:
        prepare_machine_root(self.rootdir)
        init_test_environment()
        cmd = [
            "systemd-nspawn",
            "--keep-unit",
            "-M",
            self.name,
            "-D",
            self.rootdir,
            "--register=no",
            "--resolv-conf=off",
            f"--bind=/.containers/{self.name}/nix:/nix",
            "--bind=/proc:/run/host/proc",
            "--bind=/sys:/run/host/sys",
            "--private-network",
            "--network-bridge=br0",
            self.toplevel.joinpath("init"),
        ]
        env = os.environ.copy()
        env["SYSTEMD_NSPAWN_UNIFIED_HIERARCHY"] = "1"
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, env=env)

    def get_systemd_process(self) -> int:
        if self.process is None:
            msg = "Machine not started"
            raise RuntimeError(msg)
        if self.process.stdout is None:
            msg = "Machine has no stdout"
            raise RuntimeError(msg)

        for line in self.process.stdout:
            print(line, end="")
            if (
                line.startswith("systemd[1]: Startup finished in")
                or "Welcome to NixOS" in line
            ):
                break
        else:
            msg = f"Failed to start container {self.name}"
            raise RuntimeError(msg)
        childs = (
            Path(f"/proc/{self.process.pid}/task/{self.process.pid}/children")
            .read_text()
            .split()
        )
        if len(childs) != 1:
            msg = f"Expected exactly one child process for systemd-nspawn, got {childs}"
            raise RuntimeError(msg)
        try:
            return int(childs[0])
        except ValueError as e:
            msg = f"Failed to parse child process id {childs[0]}"
            raise RuntimeError(msg) from e

    def get_unit_info(self, unit: str) -> dict[str, str]:
        proc = self.systemctl(f'--no-pager show "{unit}"')
        if proc.returncode != 0:
            msg = (
                f'retrieving systemctl info for unit "{unit}"'
                f" failed with exit code {proc.returncode}"
            )
            raise Error(msg)

        line_pattern = re.compile(r"^([^=]+)=(.*)$")

        def tuple_from_line(line: str) -> tuple[str, str]:
            match = line_pattern.match(line)
            if match is None:
                msg = f"Failed to parse line: {line}"
                raise RuntimeError(msg)
            return match[1], match[2]

        return dict(
            tuple_from_line(line)
            for line in proc.stdout.split("\n")
            if line_pattern.match(line)
        )

    def nsenter_command(self, command: str) -> list[str]:
        return [
            "nsenter",
            "--target",
            str(self.container_pid),
            "--mount",
            "--uts",
            "--ipc",
            "--net",
            "--pid",
            "--cgroup",
            "/bin/sh",
            "-c",
            command,
        ]

    def execute(
        self,
        command: str,
        check_return: bool = True,  # noqa: ARG002
        check_output: bool = True,  # noqa: ARG002
        timeout: int | None = 900,
    ) -> subprocess.CompletedProcess:
        """Execute a shell command, returning a list `(status, stdout)`.

        Commands are run with `set -euo pipefail` set:

        -   If several commands are separated by `;` and one fails, the
            command as a whole will fail.

        -   For pipelines, the last non-zero exit status will be returned
            (if there is one; otherwise zero will be returned).

        -   Dereferencing unset variables fails the command.

        -   It will wait for stdout to be closed.

        If the command detaches, it must close stdout, as `execute` will wait
        for this to consume all output reliably. This can be achieved by
        redirecting stdout to stderr `>&2`, to `/dev/console`, `/dev/null` or
        a file. Examples of detaching commands are `sleep 365d &`, where the
        shell forks a new process that can write to stdout and `xclip -i`, where
        the `xclip` command itself forks without closing stdout.

        Takes an optional parameter `check_return` that defaults to `True`.
        Setting this parameter to `False` will not check for the return code
        and return -1 instead. This can be used for commands that shut down
        the VM and would therefore break the pipe that would be used for
        retrieving the return code.

        A timeout for the command can be specified (in seconds) using the optional
        `timeout` parameter, e.g., `execute(cmd, timeout=10)` or
        `execute(cmd, timeout=None)`. The default is 900 seconds.
        """
        # Always run command with shell opts
        command = f"set -eo pipefail; source /etc/profile; set -xu; {command}"

        return subprocess.run(
            self.nsenter_command(command),
            timeout=timeout,
            check=False,
            stdout=subprocess.PIPE,
            text=True,
        )

    def nested(
        self,
        msg: str,
        attrs: dict[str, str] | None = None,
    ) -> _GeneratorContextManager:
        if attrs is None:
            attrs = {}
        my_attrs = {"machine": self.name}
        my_attrs.update(attrs)
        return self.logger.nested(msg, my_attrs)

    def systemctl(self, q: str) -> subprocess.CompletedProcess:
        """Runs `systemctl` commands with optional support for
        `systemctl --user`

        ```py
        # run `systemctl list-jobs --no-pager`
        machine.systemctl("list-jobs --no-pager")

        # spawn a shell for `any-user` and run
        # `systemctl --user list-jobs --no-pager`
        machine.systemctl("list-jobs --no-pager", "any-user")
        ```
        """
        return self.execute(f"systemctl {q}")

    def wait_until_succeeds(self, command: str, timeout: int = 900) -> str:
        """Repeat a shell command with 1-second intervals until it succeeds.
        Has a default timeout of 900 seconds which can be modified, e.g.
        `wait_until_succeeds(cmd, timeout=10)`. See `execute` for details on
        command execution.
        Throws an exception on timeout.
        """
        output = ""

        def check_success(_: Any) -> bool:
            nonlocal output
            result = self.execute(command, timeout=timeout)
            return result.returncode == 0

        with self.nested(f"waiting for success: {command}"):
            retry(check_success, timeout)
            return output

    def wait_for_open_port(
        self,
        port: int,
        addr: str = "localhost",
        timeout: int = 900,
    ) -> None:
        """Wait for a port to be open on the given address."""
        command = f"nc -z {shlex.quote(addr)} {port}"
        self.wait_until_succeeds(command, timeout=timeout)

    def wait_for_file(self, filename: str, timeout: int = 30) -> None:
        """Waits until the file exists in the machine's file system."""

        def check_file(_last_try: bool) -> bool:
            result = self.execute(f"test -e {filename}")
            return result.returncode == 0

        with self.nested(f"waiting for file '{filename}'"):
            retry(check_file, timeout)

    def wait_for_unit(self, unit: str, timeout: int = 900) -> None:
        """Wait for a systemd unit to get into "active" state.
        Throws exceptions on "failed" and "inactive" states as well as after
        timing out.
        """

        def check_active(_: bool) -> bool:
            info = self.get_unit_info(unit)
            state = info["ActiveState"]
            if state == "failed":
                proc = self.systemctl(f"--lines 0 status {unit}")
                journal = self.execute(f"journalctl -u {unit} --no-pager")
                msg = f'unit "{unit}" reached state "{state}":\n{proc.stdout}\n{journal.stdout}'
                raise Error(msg)

            if state == "inactive":
                proc = self.systemctl("list-jobs --full 2>&1")
                if "No jobs" in proc.stdout:
                    info = self.get_unit_info(unit)
                    if info["ActiveState"] == state:
                        msg = f'unit "{unit}" is inactive and there are no pending jobs'
                        raise Error(msg)

            return state == "active"

        retry(check_active, timeout)

    def succeed(self, command: str, timeout: int | None = None) -> str:
        res = self.execute(command, timeout=timeout)
        if res.returncode != 0:
            msg = f"Failed to run command {command}\n"
            msg += f"Exit code: {res.returncode}\n"
            msg += f"Stdout: {res.stdout}"
            raise RuntimeError(msg)
        return res.stdout

    def fail(self, command: str, timeout: int | None = None) -> str:
        res = self.execute(command, timeout=timeout)
        if res.returncode == 0:
            msg = f"command `{command}` unexpectedly succeeded\n"
            msg += f"Exit code: {res.returncode}\n"
            msg += f"Stdout: {res.stdout}"
            raise RuntimeError(msg)
        return res.stdout

    def shutdown(self) -> None:
        """Shut down the machine, waiting for the VM to exit."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None

    def release(self) -> None:
        self.shutdown()


@dataclass
class ContainerInfo:
    toplevel: Path
    closure_info: Path

    @cached_property
    def name(self) -> str:
        name_match = re.match(r".*-nixos-system-(.+)-(.+)", self.toplevel.name)
        if not name_match:
            msg = f"Unable to extract hostname from {self.toplevel.name}"
            raise Error(msg)
        return name_match.group(1)

    @property
    def root_dir(self) -> Path:
        return Path(f"/.containers/{self.name}")

    @property
    def nix_store_dir(self) -> Path:
        return self.root_dir / "nix" / "store"

    @property
    def etc_dir(self) -> Path:
        return self.root_dir / "etc"


def setup_filesystems(container: ContainerInfo) -> None:
    # We don't care about cleaning up the mount points, since we're running in a nix sandbox.
    Path("/run").mkdir(parents=True, exist_ok=True)
    subprocess.run(["mount", "-t", "tmpfs", "none", "/run"], check=True)
    subprocess.run(["mount", "-t", "cgroup2", "none", "/sys/fs/cgroup"], check=True)
    container.etc_dir.mkdir(parents=True)
    Path("/etc/os-release").touch()
    Path("/etc/machine-id").write_text("a5ea3f98dedc0278b6f3cc8c37eeaeac")
    container.nix_store_dir.mkdir(parents=True)
    container.nix_store_dir.chmod(0o755)

    # Recreate symlinks
    for file in Path("/nix/store").iterdir():
        if file.is_symlink():
            target = file.readlink()
            sym = container.nix_store_dir / file.name
            os.symlink(target, sym)

    # Read /proc/mounts and replicate every bind mount
    with Path("/proc/self/mounts").open() as f:
        for line in f:
            columns = line.split(" ")
            source = Path(columns[1])
            if source.parent != Path("/nix/store/"):
                continue
            target = container.nix_store_dir / source.name
            if source.is_dir():
                target.mkdir()
            else:
                target.touch()
            try:
                if "acl" in target.name:
                    print(f"mount({source}, {target})")
                mount(source, target, "none", MS_BIND)
            except OSError as e:
                msg = f"mount({source}, {target}) failed"
                raise Error(msg) from e


def load_nix_db(container: ContainerInfo) -> None:
    with (container.closure_info / "registration").open() as f:
        subprocess.run(
            ["nix-store", "--load-db", "--store", str(container.root_dir)],
            stdin=f,
            check=True,
            text=True,
        )


class Driver:
    logger: AbstractLogger

    def __init__(
        self,
        containers: list[ContainerInfo],
        logger: AbstractLogger,
        testscript: str,
        out_dir: str,
    ) -> None:
        self.containers = containers
        self.testscript = testscript
        self.out_dir = out_dir
        self.logger = logger

        self.tempdir = TemporaryDirectory()
        tempdir_path = Path(self.tempdir.name)

        self.machines = []
        for container in containers:
            setup_filesystems(container)
            load_nix_db(container)
            self.machines.append(
                Machine(
                    name=container.name,
                    toplevel=container.toplevel,
                    rootdir=tempdir_path / container.name,
                    out_dir=self.out_dir,
                    logger=self.logger,
                ),
            )

    def start_all(self) -> None:
        # Ensure test environment is set up
        init_test_environment()

        for machine in self.machines:
            print(f"Starting {machine.name}")
            machine.start()

        # Print copy-pastable nsenter command to debug container tests
        for machine in self.machines:
            nspawn_uuid = uuid.uuid4()

            # We lauch a sleep here, so we can pgrep the process cmdline for
            # the uuid
            sleep = shutil.which("sleep")
            if sleep is None:
                msg = "sleep command not found"
                raise RuntimeError(msg)
            machine.execute(
                f"systemd-run /bin/sh -c '{sleep} 999999999 && echo {nspawn_uuid}'",
            )

            print(
                f"To attach to container {machine.name} run on the same machine that runs the test:",
            )
            print(
                " ".join(
                    [
                        Style.BRIGHT,
                        Fore.CYAN,
                        "sudo",
                        "nsenter",
                        "--user",
                        "--target",
                        f"$(\\pgrep -f '^/bin/sh.*{nspawn_uuid}')",
                        "--mount",
                        "--uts",
                        "--ipc",
                        "--net",
                        "--pid",
                        "--cgroup",
                        "/bin/sh",
                        "-c",
                        "bash",
                        Style.RESET_ALL,
                    ],
                ),
            )

    def test_symbols(self) -> dict[str, Any]:
        general_symbols = {
            "start_all": self.start_all,
            "machines": self.machines,
            "driver": self,
            "Machine": Machine,  # for typing
        }
        machine_symbols = {pythonize_name(m.name): m for m in self.machines}
        # If there's exactly one machine, make it available under the name
        # "machine", even if it's not called that.
        if len(self.machines) == 1:
            (machine_symbols["machine"],) = self.machines
        print(
            "additionally exposed symbols:\n    "
            + ", ".join(m.name for m in self.machines)
            + ",\n    "
            + ", ".join(list(general_symbols.keys())),
        )
        return {**general_symbols, **machine_symbols}

    def test_script(self) -> None:
        """Run the test script"""
        exec(self.testscript, self.test_symbols(), None)  # noqa: S102

    def run_tests(self) -> None:
        """Run the test script (for non-interactive test runs)"""
        self.test_script()

    def __enter__(self) -> "Driver":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        for machine in self.machines:
            machine.release()


def writeable_dir(arg: str) -> Path:
    """Raises an ArgumentTypeError if the given argument isn't a writeable directory
    Note: We want to fail as early as possible if a directory isn't writeable,
    since an executed nixos-test could fail (very late) because of the test-driver
    writing in a directory without proper permissions.
    """
    path = Path(arg)
    if not path.is_dir():
        msg = f"{path} is not a directory"
        raise argparse.ArgumentTypeError(msg)
    if not os.access(path, os.W_OK):
        msg = f"{path} is not a writeable directory"
        raise argparse.ArgumentTypeError(msg)
    return path


def main() -> None:
    arg_parser = argparse.ArgumentParser(prog="nixos-test-driver")
    arg_parser.add_argument(
        "--containers",
        nargs=2,
        action="append",
        type=Path,
        metavar=("TOPLEVEL_STORE_DIR", "CLOSURE_INFO"),
        help="container system toplevel store dir and closure info",
    )
    arg_parser.add_argument(
        "--test-script",
        help="the test script to run",
        type=Path,
    )
    arg_parser.add_argument(
        "-o",
        "--output-directory",
        default=Path.cwd(),
        help="the directory to bind to /run/test-results",
        type=writeable_dir,
    )
    args = arg_parser.parse_args()
    logger = CompositeLogger([TerminalLogger()])
    with Driver(
        containers=[
            ContainerInfo(toplevel, closure_info)
            for toplevel, closure_info in args.containers
        ],
        testscript=args.test_script.read_text(),
        out_dir=args.output_directory.resolve(),
        logger=logger,
    ) as driver:
        driver.run_tests()
