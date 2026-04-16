#!/usr/bin/env python3
"""Network status display for terminal.

Displays network interface addresses, VPN status, Tor onion addresses,
and mDNS hostname. Designed to run inside kmscon as the login shell.
"""

from __future__ import annotations

import argparse
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# ANSI escape codes
BOLD_UNDERLINE = "\033[1;4m"
RESET = "\033[0m"

# Matches CSI SGR sequences (colors, bold, etc.) emitted by `ip -color`
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    """Remove ANSI SGR escape sequences from text."""
    return _ANSI_RE.sub("", text)


# VPN interface name patterns (prefix match)
VPN_NAME_PATTERNS = ["ygg", "zt", "mycelium", "tailscale"]

# Tor service directories to scan for .onion addresses
TOR_SERVICE_DIRS = [
    "/var/lib/tor/onion-service",  # Default NixOS location
    "/var/lib/tor",  # Some services put them directly here
    "/run/secrets",  # Clan vars secret store
]

# Clan logo using block characters (with signature dot on C)
CLAN_LOGO = """\n
  ██████ ██       █████  ███    ██
 ██      ██      ██   ██ ████   ██
 ██      ██      ███████ ██ ██  ██
 ██      ██      ██   ██ ██  ██ ██
  ██████ ███████ ██   ██ ██   ████
██                               """


def clear_screen() -> None:
    """Clear terminal and move cursor to home."""
    print("\033[2J\033[H", end="", flush=True)


def get_terminal_width() -> int:
    """Get terminal width, defaulting to 80 if unavailable."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:  # noqa: BLE001
        return 80


def center_text(text: str, width: int) -> str:
    """Center text block within the given width.

    Uses the width of the longest line to calculate padding,
    so the entire block is centered as a unit.
    """
    lines = text.splitlines()
    if not lines:
        return ""
    max_len = max(len(line) for line in lines)
    padding = max(0, (width - max_len) // 2)
    return "\n".join(" " * padding + line for line in lines)


def get_hostname() -> str:
    """Read hostname from /etc/hostname."""
    try:
        return Path("/etc/hostname").read_text().strip()
    except (OSError, UnicodeDecodeError):
        return "nixos"


def get_ip_addresses() -> list[str]:
    """Get network interface addresses using `ip -brief -color addr`.

    Filters out the `lo` interface, interfaces not in state UP, and
    link-local IPv6 addresses (`fe80::`).
    """
    try:
        result = subprocess.run(
            ["ip", "-brief", "-color", "addr"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return ["(ip command not found)"]

    addrs = []
    for line in result.stdout.splitlines():
        fields = _strip_ansi(line).split()
        min_fields_for_state = 2
        if len(fields) < min_fields_for_state:
            continue
        iface, state = fields[0], fields[1]
        if iface == "lo" or state != "UP":
            continue
        display_parts = [p for p in line.split() if "fe80" not in _strip_ansi(p)]
        addrs.append(" ".join(display_parts))
    return addrs


def detect_vpn_interfaces() -> list[str]:
    """Detect VPN interfaces automatically.

    Uses two methods:
    1. `ip link show type wireguard` for WireGuard interfaces
    2. Name pattern matching for ZeroTier (zt*), Yggdrasil (ygg), Mycelium
    """
    interfaces: list[str] = []

    # Method 1: Detect WireGuard interfaces by type
    try:
        result = subprocess.run(
            ["ip", "link", "show", "type", "wireguard"],
            capture_output=True,
            text=True,
            check=False,
        )
        for line in result.stdout.splitlines():
            # Parse: "N: interface_name: <FLAGS>" or "N: interface_name@carrier: <FLAGS>"
            if ": " in line:
                parts = line.split()
                min_parts_for_interface_name = 2
                if len(parts) >= min_parts_for_interface_name:
                    name_part = parts[1].rstrip(":")
                    name = name_part.split("@")[0]
                    if name and name not in interfaces:
                        interfaces.append(name)
    except FileNotFoundError:
        pass

    # Method 2: Scan /sys/class/net for known VPN name patterns
    net_dir = Path("/sys/class/net")
    if net_dir.exists():
        for iface in net_dir.iterdir():
            name = iface.name
            if name in interfaces:
                continue
            if any(name.startswith(pattern) for pattern in VPN_NAME_PATTERNS):
                interfaces.append(name)

    interfaces.sort()
    return interfaces


def get_vpn_addresses(interfaces: list[str]) -> list[str]:
    """Get addresses for VPN interfaces."""
    addrs = []
    for iface in interfaces:
        try:
            result = subprocess.run(
                ["ip", "-brief", "-color", "addr", "show", iface],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            addrs.append(f"{iface} (ip command not found)")
            continue

        line = result.stdout.strip()
        if not line:
            addrs.append(f"{iface} OFFLINE")
            continue

        fields = _strip_ansi(line).split()
        min_fields_for_state = 2
        if len(fields) < min_fields_for_state:
            addrs.append(f"{iface} OFFLINE")
            continue

        state = fields[1]
        # UP or UNKNOWN — UNKNOWN is common for virtual VPN interfaces
        if state not in ("UP", "UNKNOWN"):
            addrs.append(f"{iface} OFFLINE")
            continue

        # Filter fe80:: link-local from display while preserving color codes
        display_parts = [p for p in line.split() if "fe80" not in _strip_ansi(p)]
        routable = [a for a in fields[2:] if "fe80" not in a]
        if routable:
            addrs.append(" ".join(display_parts))
        else:
            addrs.append(f"{iface} UP (no addresses)")
    return addrs


def read_onion_address(path: Path) -> str | None:
    """Read a .onion address from a hostname file."""
    try:
        content = path.read_text().strip()
    except (OSError, UnicodeDecodeError):
        return None
    if content.endswith(".onion"):
        return content
    return None


def get_tor_addresses(explicit_paths: list[str]) -> list[str]:
    """Detect Tor hidden service .onion addresses.

    If explicit paths are provided via --tor-address, reads from those files
    in the given order. Otherwise scans known Tor data directories for
    hostname files and returns them sorted for stable display.
    """
    tor_addrs: list[str] = []

    for path_str in explicit_paths:
        addr = read_onion_address(Path(path_str))
        if addr and addr not in tor_addrs:
            tor_addrs.append(addr)

    if explicit_paths:
        return tor_addrs

    auto_detected: list[str] = []
    for base_dir in TOR_SERVICE_DIRS:
        base_path = Path(base_dir)
        try:
            if not base_path.exists():
                continue
        except OSError:
            continue

        direct_hostname = base_path / "hostname"
        addr = read_onion_address(direct_hostname)
        if addr and addr not in auto_detected:
            auto_detected.append(addr)

        # Scan subdirectories: e.g. /var/lib/tor/onion-service/clan_default/hostname
        try:
            entries = list(base_path.iterdir())
        except OSError:
            continue
        for entry in entries:
            try:
                if not entry.is_dir():
                    continue
            except OSError:
                continue
            addr = read_onion_address(entry / "hostname")
            if addr and addr not in auto_detected:
                auto_detected.append(addr)

    auto_detected.sort()
    return auto_detected


def print_status(
    ip_addrs: list[str],
    vpn_addrs: list[str],
    tor_addrs: list[str],
    hostname: str,
) -> None:
    """Print formatted network status to terminal."""
    term_width = get_terminal_width()

    # Print centered logo
    print(center_text(CLAN_LOGO, term_width))
    print()

    # Network Information section
    print(f"  {BOLD_UNDERLINE}Network Information{RESET}")
    for addr in ip_addrs:
        print(f"    {addr}")

    # VPN Networks section
    if vpn_addrs:
        print()
        print(f"  {BOLD_UNDERLINE}VPN Networks{RESET}")
        for addr in vpn_addrs:
            print(f"    {addr}")

    # Tor Hidden Services section
    if tor_addrs:
        print()
        print(f"  {BOLD_UNDERLINE}Tor Hidden Services{RESET}")
        for addr in tor_addrs:
            print(f"    {addr}")

    # Multicast DNS section
    print()
    print(f"  {BOLD_UNDERLINE}Multicast DNS{RESET}")
    print(f"    {hostname}.local")

    # Footer
    print()
    print("  " + "\u2500" * 50)  # Unicode box-drawing horizontal line
    print("  Press 'Ctrl-C' for console access")


def parse_args(args: list[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="network-status",
        description="Display network status information on terminal.",
        epilog=(
            "If no --vpn is specified, VPN interfaces are auto-detected "
            "(WireGuard, ZeroTier, Yggdrasil, Mycelium).\n\n"
            "If no --tor-address is specified, .onion addresses are "
            "auto-discovered from standard Tor service directories."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--vpn",
        action="append",
        default=[],
        metavar="INTERFACE",
        help="VPN interface to monitor (can be repeated)",
    )
    parser.add_argument(
        "--tor-address",
        action="append",
        default=[],
        metavar="PATH",
        help="path to file containing .onion address (can be repeated)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="print status once and exit (for testing)",
    )
    return parser.parse_args(args)


def main() -> None:
    """Main loop: poll and display network status."""
    args = parse_args(sys.argv[1:])

    # Auto-detect VPN interfaces if none specified
    vpn_interfaces: list[str] = args.vpn
    if not vpn_interfaces:
        vpn_interfaces = detect_vpn_interfaces()
    tor_address_paths: list[str] = args.tor_address
    once_mode: bool = args.once

    running = True

    def handle_sigint(_sig: int, _frame: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, handle_sigint)

    last_ip_addrs: list[str] | None = None
    last_vpn_addrs: list[str] | None = None
    last_tor_addrs: list[str] | None = None
    last_hostname: str | None = None

    while running:
        ip_addrs = get_ip_addresses()
        vpn_addrs = get_vpn_addresses(vpn_interfaces)
        tor_addrs = get_tor_addresses(tor_address_paths)
        hostname = get_hostname()

        # Only redraw if state changed
        state_changed = (
            ip_addrs != last_ip_addrs
            or vpn_addrs != last_vpn_addrs
            or tor_addrs != last_tor_addrs
            or hostname != last_hostname
        )

        if state_changed:
            if not once_mode:
                clear_screen()
            print_status(
                ip_addrs=ip_addrs,
                vpn_addrs=vpn_addrs,
                tor_addrs=tor_addrs,
                hostname=hostname,
            )
            last_ip_addrs = ip_addrs
            last_vpn_addrs = vpn_addrs
            last_tor_addrs = tor_addrs
            last_hostname = hostname

        if once_mode:
            break

        # Sleep in small increments to respond to Ctrl-C quickly
        for _ in range(20):  # 2 seconds total (20 * 0.1s)
            if not running:
                break
            time.sleep(0.1)

    # Clear screen on exit (but not in --once mode, where the user wants to see output)
    if not once_mode:
        clear_screen()


if __name__ == "__main__":
    main()
