import os


def is_flatpak() -> bool:
    """Check if the current process is running inside a flatpak sandbox."""
    # FLATPAK_ID environment variable check
    flatpak_env = "FLATPAK_ID" in os.environ

    flatpak_file = False
    try:
        with open("/.flatpak-info"):
            flatpak_file = True
    except FileNotFoundError:
        pass

    return flatpak_env and flatpak_file
