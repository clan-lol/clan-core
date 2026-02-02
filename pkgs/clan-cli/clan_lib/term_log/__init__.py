import logging
from typing import Any

log = logging.getLogger(__name__)


def log_machine(msg: str, *a: object, **kw: Any) -> None:
    machine_name = kw.pop("machine_name", "unknown")
    log.info(msg, *a, extra={"command_prefix": machine_name}, **kw)
