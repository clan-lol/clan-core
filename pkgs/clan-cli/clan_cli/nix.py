import os

CLAN_NIXPKGS = os.environ.get("CLAN_NIXPKGS")


def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    # in unittest we will have all binaries provided
    if CLAN_NIXPKGS is None:
        return cmd
    return ["nix", "shell", "-f", CLAN_NIXPKGS] + packages + ["-c"] + cmd
