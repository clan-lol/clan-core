from clan_lib.version import read_version

DOCS_BASE_URL = "https://clan.lol/docs"
"""Root URL of the clan.lol documentation site, without a version segment."""

DOCS_VERSION = read_version()
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
