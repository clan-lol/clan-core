import logging
from typing import Any, Callable
from pathlib import Path

grey = "\x1b[38;20m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
bold_red = "\x1b[31;1m"
green = "\u001b[32m"
blue = "\u001b[34m"


def get_formatter(color: str) -> Callable[[logging.LogRecord], logging.Formatter]:
    def myformatter(record: logging.LogRecord) -> logging.Formatter:
        reset = "\x1b[0m"
        filepath = Path(record.pathname).resolve()
        return logging.Formatter(
            f"{filepath}:%(lineno)d::%(funcName)s\n{color}%(levelname)s{reset}: %(message)s"
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
        return FORMATTER[record.levelno](record).format(record)


def register(level: Any) -> None:
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(CustomFormatter())
    logging.basicConfig(level=level, handlers=[ch])
