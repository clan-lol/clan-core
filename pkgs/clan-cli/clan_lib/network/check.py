import logging
from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.cmd import ClanCmdError, ClanCmdTimeoutError, RunOpts, run
from clan_lib.errors import ClanError  # Assuming these are available
from clan_lib.nix import nix_shell
from clan_lib.ssh.remote import Remote

cmdlog = logging.getLogger(__name__)


@dataclass(frozen=True)
class ConnectionOptions:
    timeout: int = 20


@API.register
def check_machine_ssh_login(
    remote: Remote,
    opts: ConnectionOptions | None = None,
) -> None:
    """Checks if a remote machine is reachable via SSH by attempting to run a simple command.

    Args:
        remote (Remote): The remote host to check for SSH login.
        opts (ConnectionOptions, optional): Connection options such as timeout.
            If not provided, default values are used.
    Usage:
        result = check_machine_ssh_login(remote)
        if result.ok:
            print("SSH login successful")
        else:
            print(f"SSH login failed: {result.reason}")

    Raises:
        ClanError: If the SSH login fails.

    """
    if opts is None:
        opts = ConnectionOptions()

    with remote.host_connection() as ssh:
        try:
            ssh.run(
                ["true"],
                RunOpts(timeout=opts.timeout, needs_user_terminal=True),
            )
        except ClanCmdTimeoutError as e:
            msg = f"SSH login timeout after {opts.timeout}s"
            raise ClanError(msg) from e
        except ClanCmdError as e:
            if "Host key verification failed." in e.cmd.stderr:
                raise ClanError(e.cmd.stderr.strip()) from e
            msg = f"SSH login failed: {e}"
            raise ClanError(msg) from e
        else:
            return


@API.register
def check_machine_ssh_reachable(
    remote: Remote,
    opts: ConnectionOptions | None = None,
) -> None:
    """Checks if a remote machine is reachable via SSH by attempting to open a TCP connection
    to the specified address and port.

    Args:
        remote (Remote): The remote host to check for SSH reachability.
        opts (ConnectionOptions, optional): Connection options such as timeout.
            If not provided, default values are used.

    Returns:
        CheckResult: An object indicating whether the SSH port is reachable (`ok=True`) or not (`ok=False`),
        and a reason if the check failed.
    Usage:
        result = check_machine_ssh_reachable(remote)
        if result.ok:
            print("SSH port is reachable")
            print(f"SSH port is not reachable: {result.reason}")

    """
    if opts is None:
        opts = ConnectionOptions()

    cmdlog.debug(
        f"Checking SSH reachability for {remote.target} on port {remote.port or 22}",
    )

    cmd = [
        "nc",
    ]

    # If using SOCKS5 proxy, add -x
    if remote.socks_port:
        cmd.extend(
            [
                "-X",
                "5",
                "-x",
                f"localhost:{remote.socks_port}",
            ],
        )

    cmd.extend(
        [
            "-z",
            "-w",
            str(opts.timeout),
            str(remote.address.strip()),
            str(remote.port or 22),
        ],
    )

    try:
        res = run(
            nix_shell(["netcat"], cmd),
            options=RunOpts(timeout=opts.timeout, check=False),
        )

        if "succeeded" in res.stderr:
            return

        msg = "Connection failed: SSH server not reachable"
        raise ClanError(msg)

    except ClanCmdTimeoutError as e:
        msg = f"Connection timeout after {opts.timeout}s"
        raise ClanError(msg) from e
