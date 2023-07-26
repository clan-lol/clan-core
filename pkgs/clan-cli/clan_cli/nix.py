import os


def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    flake = os.environ.get("CLAN_FLAKE")
    # in unittest we will have all binaries provided
    if flake is None:
        return cmd
    wrapped_packages = [f"path:{flake}#{p}" for p in packages]
    return ["nix", "shell"] + wrapped_packages + ["-c"] + cmd
