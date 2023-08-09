import argparse

from clan_cli.secrets import register_parser


class SecretCli:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        register_parser(self.parser)

    def run(self, args: list[str]) -> argparse.Namespace:
        parsed = self.parser.parse_args(args)
        parsed.func(parsed)
        return parsed
