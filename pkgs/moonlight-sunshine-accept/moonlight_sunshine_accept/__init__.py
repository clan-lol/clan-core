#!/usr/bin/env python

import argparse

from . import moonlight, sunshine


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="moonlight-sunshine-accept",
        description="Manage moonlight machines",
    )
    subparsers = parser.add_subparsers()

    parser_sunshine = subparsers.add_parser(
        "sunshine",
        aliases=["sun"],
        description="Sunshine configuration",
        help="Sunshine configuration",
    )
    sunshine.register_parser(parser_sunshine)

    parser_moonlight = subparsers.add_parser(
        "moonlight",
        aliases=["moon"],
        description="Moonlight configuration",
        help="Moonlight configuration",
    )
    moonlight.register_parser(parser_moonlight)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
