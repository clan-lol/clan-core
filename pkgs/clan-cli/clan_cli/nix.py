import os


def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    nixpkgs = os.environ.get("CLAN_NIXPKGS")
    # in unittest we will have all binaries provided
    if nixpkgs is None:
        return cmd
    wrapped_packages = [f"path:{nixpkgs}#{p}" for p in packages]
    return ["nix", "shell"] + wrapped_packages + ["-c"] + cmd
