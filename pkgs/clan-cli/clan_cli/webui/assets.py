import functools
import logging
from pathlib import Path

log = logging.getLogger(__name__)


def get_hash(string: str) -> str:
    """
    This function takes a string like '/nix/store/kkvk20b8zh8aafdnfjp6dnf062x19732-source'
    and returns the hash part 'kkvk20b8zh8aafdnfjp6dnf062x19732' after '/nix/store/' and before '-source'.
    """
    # Split the string by '/' and get the last element
    last_element = string.split("/")[-1]
    # Split the last element by '-' and get the first element
    hash_part = last_element.split("-")[0]
    # Return the hash part
    return hash_part


def check_divergence(path: Path) -> None:
    p = path.resolve()

    log.info("Absolute web asset path: %s", p)
    if not p.is_dir():
        raise FileNotFoundError(p)

    # Get the hash part of the path
    gh = get_hash(str(p))

    log.debug(f"Serving webui asset with hash {gh}")


@functools.cache
def asset_path() -> Path:
    path = Path(__file__).parent / "assets"
    log.debug("Serving assets from: %s", path)
    check_divergence(path)
    return path
