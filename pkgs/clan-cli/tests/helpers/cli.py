import argparse

from clan_cli import create_parser


class Cli:
    def __init__(self) -> None:
        self.parser = create_parser(prog="clan")

    def run(self, args: list[str]) -> argparse.Namespace:
        parsed = self.parser.parse_args(args)
        if hasattr(parsed, "func"):
            parsed.func(parsed)
        return parsed
