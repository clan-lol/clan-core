import argparse
import logging

from clan_lib.flash.list import list_keymaps, list_languages

log = logging.getLogger(__name__)


def list_command(args: argparse.Namespace) -> None:
    if args.cmd == "languages":
        languages = list_languages()
        for language in languages:
            print(language)
    elif args.cmd == "keymaps":
        keymaps = list_keymaps()
        for keymap in keymaps:
            print(keymap)


def register_flash_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "cmd",
        choices=["languages", "keymaps"],
        type=str,
        help="list possible languages or keymaps",
    )

    parser.set_defaults(func=list_command)
