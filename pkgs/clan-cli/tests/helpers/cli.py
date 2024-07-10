import argparse
import logging
import shlex

from clan_cli import create_parser
from clan_cli.custom_logger import get_caller

log = logging.getLogger(__name__)


def run(args: list[str]) -> argparse.Namespace:
    parser = create_parser(prog="clan")
    parsed = parser.parse_args(args)
    cmd = shlex.join(["clan", *args])
    log.debug(f"$ {cmd} \nCaller: {get_caller()}")
    if hasattr(parsed, "func"):
        parsed.func(parsed)
    return parsed
