import argparse
import logging
import shlex

from clan_cli import create_parser
from clan_cli.custom_logger import get_caller

log = logging.getLogger(__name__)


class Cli:
    def run(self, args: list[str]) -> argparse.Namespace:
        parser = create_parser(prog="clan")
        cmd = shlex.join(["clan", *args])
        log.debug(f"$ {cmd}")
        log.debug(f"Caller {get_caller()}")
        parsed = parser.parse_args(args)
        if hasattr(parsed, "func"):
            parsed.func(parsed)
        return parsed
