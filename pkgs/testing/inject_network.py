#!/usr/bin/env python3
"""Inject external network into a running container test.

This script is used to debug hermetic container tests that need network access
to identify missing store paths. It works with the container test framework's
wait_for_signal() helper.

Usage:
  1. Add wait_for_signal() to your test script where you want to pause:

       start_all()
       machine.wait_for_unit("multi-user.target")
       wait_for_signal()  # Pauses here
       # ... rest of test

  2. Run the test: nix build .#checks.x86_64-linux.yourTest -L

  3. When paused, the test prints a UUID. Run this script with that UUID:
       ./inject-network.py <uuid>

  4. Now you can SSH into the container and run:
       nix build --dry-run .#yourPackage
     to see which paths would be fetched (these are missing from closureInfo)

  5. Press Ctrl-C to clean up and signal the test to continue.
"""

import os
import signal
import subprocess
import sys
from collections.abc import Generator
from contextlib import contextmanager, suppress
from pathlib import Path


def sudo(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["sudo", *args], check=check, capture_output=True, text=True)


def nsenter(
    pid: int, ns: str, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return sudo(
        "nsenter", "--user", f"--{ns}", "--target", str(pid), "--", *args, check=check
    )


def pgrep(pattern: str) -> int | None:
    r = subprocess.run(
        ["pgrep", "-f", pattern], capture_output=True, text=True, check=False
    )
    return int(r.stdout.split()[0]) if r.returncode == 0 and r.stdout.strip() else None


def find_test_driver(pid: int) -> int | None:
    """Walk up the process tree to find the nixos-test-driver process."""
    while pid > 1:
        try:
            stat = Path(f"/proc/{pid}/stat").read_text()
            ppid = int(stat.split(")")[1].split()[1])
            cmdline = Path(f"/proc/{pid}/cmdline").read_text()
            if "nixos-test-driver" in cmdline:
                return pid
            pid = ppid
        except (FileNotFoundError, PermissionError, IndexError, ValueError):
            return None
    return None


@contextmanager
def network_injection(
    pid: int, subnet: str, veth_host: str, veth_inject: str
) -> Generator[None]:
    """Set up and tear down network injection."""
    print("Setting up network...")
    sudo("ip", "link", "add", veth_host, "type", "veth", "peer", "name", veth_inject)
    try:
        sudo("ip", "link", "set", veth_inject, "netns", f"/proc/{pid}/ns/net")
        sudo("ip", "addr", "add", f"{subnet}.1/24", "dev", veth_host)
        sudo("ip", "link", "set", veth_host, "up")
        nsenter(pid, "net", "ip", "addr", "add", f"{subnet}.2/24", "dev", veth_inject)
        nsenter(pid, "net", "ip", "link", "set", veth_inject, "up")
        nsenter(pid, "net", "ip", "route", "add", "default", "via", f"{subnet}.1")
        nsenter(
            pid, "mount", "sh", "-c", 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
        )
        sudo("sysctl", "-w", "net.ipv4.ip_forward=1")
        sudo(
            "iptables",
            "-t",
            "nat",
            "-A",
            "POSTROUTING",
            "-s",
            f"{subnet}.0/24",
            "-j",
            "MASQUERADE",
        )
        ok = (
            nsenter(
                pid, "net", "ping", "-c", "1", "-W", "2", "8.8.8.8", check=False
            ).returncode
            == 0
        )
        print(f"{'✓' if ok else '✗'} Network {'ready' if ok else 'may not work'}")
        yield
    finally:
        print("Cleaning up...")
        sudo(
            "iptables",
            "-t",
            "nat",
            "-D",
            "POSTROUTING",
            "-s",
            f"{subnet}.0/24",
            "-j",
            "MASQUERADE",
            check=False,
        )
        sudo("ip", "link", "del", veth_host, check=False)


EXPECTED_ARGS = 2


def main() -> int:
    if len(sys.argv) != EXPECTED_ARGS:
        print(f"Usage: {sys.argv[0]} <container-uuid>", file=sys.stderr)
        return 1

    uuid, short_id = sys.argv[1], str(os.getpid())[-4:]
    veth_host, veth_inject = f"veth-h{short_id}", f"veth-i{short_id}"
    subnet = f"10.99.{int(short_id) % 100}"

    pid = pgrep(f"^/bin/sh.*{uuid}")
    if not pid:
        print(f"Error: No container with UUID {uuid}", file=sys.stderr)
        return 1
    print(f"Container PID: {pid}")

    driver_pid = find_test_driver(pid)

    if driver_pid:
        print(f"Signaling test driver (PID {driver_pid}) to continue...")
        sudo("kill", "-USR1", str(driver_pid), check=False)

    with network_injection(pid, subnet, veth_host, veth_inject):
        print("Press Ctrl-C to clean up...")
        with suppress(KeyboardInterrupt):
            signal.pause()

    return 0


if __name__ == "__main__":
    sys.exit(main())
