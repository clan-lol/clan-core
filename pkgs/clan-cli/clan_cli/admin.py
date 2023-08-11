# !/usr/bin/env python3
import argparse
import os
import subprocess


def create(args: argparse.Namespace) -> None:
    os.makedirs(args.folder, exist_ok=True)
    # TODO create clan template in flake
    subprocess.Popen(
        [
            "nix",
            "flake",
            "init",
            "-t",
            "git+https://git.clan.lol/clan/clan-core#new-clan",
        ]
    )


def git(args: argparse.Namespace) -> None:
    subprocess.Popen(
        [
            "git",
            "-C",
            args.folder,
        ]
        + args.git_args
    )


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f",
        "--folder",
        help="the folder where the clan is defined, default to the current folder",
        default=os.environ["PWD"],
    )
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    parser_create = subparser.add_parser("create", help="create a new clan")
    parser_create.set_defaults(func=create)

    parser_git = subparser.add_parser("git", help="control the clan repo via git")
    parser_git.add_argument("git_args", nargs="*")
    parser_git.set_defaults(func=git)
