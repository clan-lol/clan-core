import os


def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    nixpkgs = os.environ.get("CLAN_NIXPKGS")
    # in unittest we will have all binaries provided
    if nixpkgs is None:
        return cmd
    return ["nix", "shell", "-f", nixpkgs] + packages + ["-c"] + cmd
