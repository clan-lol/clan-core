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

        try:
            filepath = Path(record.pathname).resolve()
            filepath = Path("~", filepath.relative_to(Path.home()))
        except Exception:
            filepath = Path(record.pathname)

        if not with_location:
            return logging.Formatter(f"{color}%(levelname)s{reset}: %(message)s")

        return logging.Formatter(
            f"{color}%(levelname)s{reset}: %(message)s\nLocation: {filepath}:%(lineno)d::%(funcName)s\n"
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
    def __init__(self, log_locations: bool) -> None:
        super().__init__()
        self.log_locations = log_locations

    def format(self, record: logging.LogRecord) -> str:
        return FORMATTER[record.levelno](record, self.log_locations).format(record)


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

    try:
        filepath = Path(frame_info.filename).resolve()
        filepath = Path("~", filepath.relative_to(Path.home()))
    except Exception:
        filepath = Path(frame_info.filename)

    ret = f"{filepath}:{frame_info.lineno}::{frame_info.function}"
    return ret


def setup_logging(level: Any, root_log_name: str = __name__.split(".")[0]) -> None:
    # Get the root logger and set its level
    main_logger = logging.getLogger(root_log_name)
    main_logger.setLevel(level)

    # Create and add the default handler
    default_handler = logging.StreamHandler()

    # Create and add your custom handler
    default_handler.setLevel(level)
    default_handler.setFormatter(CustomFormatter(str(level) == str(logging.DEBUG)))
    main_logger.addHandler(default_handler)

    # Set logging level for other modules used by this module
    logging.getLogger("asyncio").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(level=logging.WARNING)
