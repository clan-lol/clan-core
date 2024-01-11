import argparse
import logging
import shlex

from clan_cli import create_parser
from clan_cli.custom_logger import get_caller, setup_logging

log = logging.getLogger(__name__)


class Cli:
    def run(self, args: list[str]) -> argparse.Namespace:
        parser = create_parser(prog="clan")
        parsed = parser.parse_args(args)
        setup_logging(logging.DEBUG)
        cmd = shlex.join(["clan", "--debug", *args])
        log.debug(f"$ {cmd}")
        log.debug(f"Caller {get_caller()}")
        if hasattr(parsed, "func"):
            parsed.func(parsed)
        return parsed
