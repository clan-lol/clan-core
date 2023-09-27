import logging
from typing import Any

grey = "\x1b[38;20m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
bold_red = "\x1b[31;1m"
green = "\u001b[32m"
blue = "\u001b[34m"


def get_formatter(color: str) -> logging.Formatter:
    reset = "\x1b[0m"
    return logging.Formatter(
        f"{color}%(levelname)s{reset}:(%(filename)s:%(lineno)d): %(message)s"
    )


FORMATTER = {
    logging.DEBUG: get_formatter(blue),
    logging.INFO: get_formatter(green),
    logging.WARNING: get_formatter(yellow),
    logging.ERROR: get_formatter(red),
    logging.CRITICAL: get_formatter(bold_red),
}


class CustomFormatter(logging.Formatter):
    def format(self, record: Any) -> str:
        return FORMATTER[record.levelno].format(record)


def register(level: Any) -> None:
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(CustomFormatter())
    logging.basicConfig(level=level, handlers=[ch])
