import logging
from typing import Any

log = logging.getLogger(__name__)


def log_prefixed(msg: str, *a: object, **kw: Any) -> None:
    prefix = kw.pop("prefix", "unknown")
    log.info(msg, *a, extra={"command_prefix": str(prefix)}, **kw)
