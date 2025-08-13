from dataclasses import dataclass


@dataclass(frozen=True)
class SocksWrapper:
    """Configuration for SOCKS proxy wrapper commands."""

    # The command to execute for wrapping network connections through SOCKS (e.g., ["torify"])
    cmd: list[str]

    # Nix packages required to provide the wrapper command (e.g., ["tor", "torsocks"])
    packages: list[str]


# Pre-configured Tor wrapper instance
tor_wrapper = SocksWrapper(cmd=["torify"], packages=["tor", "torsocks"])
