import inspect
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

grey = "\x1b[38;20m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
bold_red = "\x1b[31;1m"
green = "\u001b[32m"
blue = "\u001b[34m"


def get_formatter(color: str) -> Callable[[logging.LogRecord, bool], logging.Formatter]:
    def myformatter(
        record: logging.LogRecord, with_location: bool
    ) -> logging.Formatter:
        reset = "\x1b[0m"
        filepath = Path(record.pathname).resolve()
        if not with_location:
            return logging.Formatter(f"{color}%(levelname)s{reset}: %(message)s")

        return logging.Formatter(
            f"{color}%(levelname)s{reset}: %(message)s\n       {filepath}:%(lineno)d::%(funcName)s\n"
        )

    return myformatter


FORMATTER = {
    logging.DEBUG: get_formatter(blue),
    logging.INFO: get_formatter(green),
    logging.WARNING: get_formatter(yellow),
    logging.ERROR: get_formatter(red),
    logging.CRITICAL: get_formatter(bold_red),
}


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return FORMATTER[record.levelno](record, True).format(record)


class ThreadFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return FORMATTER[record.levelno](record, False).format(record)


def get_caller() -> str:
    frame = inspect.currentframe()
    if frame is None:
        return "unknown"
    caller_frame = frame.f_back
    if caller_frame is None:
        return "unknown"
    caller_frame = caller_frame.f_back
    if caller_frame is None:
        return "unknown"
    frame_info = inspect.getframeinfo(caller_frame)
    ret = f"{frame_info.filename}:{frame_info.lineno}::{frame_info.function}"
    return ret


def setup_logging(level: Any) -> None:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(CustomFormatter())
    logger = logging.getLogger("registerHandler")
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(level=logging.WARNING)
    logger.addHandler(handler)
    # logging.basicConfig(level=level, handlers=[handler])
