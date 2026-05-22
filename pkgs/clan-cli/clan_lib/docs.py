from pathlib import Path

DOCS_BASE_URL = "https://clan.lol/docs"
"""Root URL of the clan.lol documentation site, without a version segment."""


def _read_docs_version() -> str:
    """Return the docs version from the repository's ``VERSION`` file.

    The file lives at the repo root. The clan-cli build copies it next to this
    module so the value is also available in the installed package and the
    pytest source tree.
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


DOCS_VERSION = _read_docs_version()
"""Documentation branch this CLI links to, read from the repo ``VERSION`` file."""


def _docs_root() -> str:
    return f"{DOCS_BASE_URL}/{DOCS_VERSION}"


def guides_url(page: str) -> str:
    page = page.strip("/")
    if not page:
        return _docs_root()
    return f"{_docs_root()}/{page}"


def reference_url(page: str) -> str:
    return f"{_docs_root()}/reference/{page.strip('/')}"


def service_url(name: str) -> str:
    return f"{_docs_root()}/services/official/{name.strip('/')}"
