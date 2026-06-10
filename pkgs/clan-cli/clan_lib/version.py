from pathlib import Path


def read_version() -> str:
    """Return the clan-core version string from the repository's ``VERSION`` file.

    ``unstable`` tracks the main branch; a release like ``26.05`` tracks that
    git tag. The file lives at the repo root. The clan-cli build copies it next
    to ``clan_lib`` so the value is also available in the installed package and
    the pytest source tree.
    """
    module_dir = Path(__file__).resolve().parent
    candidates = (
        module_dir / "VERSION",  # bundled into the package and test source
        module_dir.parents[2] / "VERSION",  # repo root, for in-tree runs
    )
    for path in candidates:
        if path.is_file():
            version = path.read_text().strip()
            if version:
                return version
    looked_in = "\n  ".join(str(path) for path in candidates)
    msg = f"Could not find the VERSION file. Looked in:\n  {looked_in}"
    raise FileNotFoundError(msg)
