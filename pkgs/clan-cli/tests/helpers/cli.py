import argparse

from clan_cli import create_parser
import logging
import sys
import shlex
log = logging.getLogger(__name__)

class Cli:
    def __init__(self) -> None:
        self.parser = create_parser(prog="clan")

    def run(self, args: list[str]) -> argparse.Namespace:
        cmd = shlex.join(["clan"] + args)
        log.debug(f"Command: {cmd}")
        parsed = self.parser.parse_args(args)
        if hasattr(parsed, "func"):
            parsed.func(parsed)
        return parsed
