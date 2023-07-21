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
            "git+https://git.clan.lol/clan/clan-core#clan-template",
        ]
    )


def edit(args: argparse.Namespace) -> None:  # pragma: no cover
    # TODO add some cli options to change certain options without relying on a text editor
    clan_flake = f"{args.folder}/flake.nix"
    if os.path.isfile(clan_flake):
        subprocess.Popen(
            [
                os.environ["EDITOR"],
                clan_flake,
            ]
        )
    else:
        print(
            f"{args.folder} has no flake.nix, so it does not seem to be the clan root folder",
        )


def rebuild(args: argparse.Namespace) -> None:  # pragma: no cover
    # TODO get clients from zerotier cli?
    if args.host:
        print(f"would redeploy {args.host} from clan {args.folder}")
    else:
        print(f"would redeploy all hosts from clan {args.folder}")


def destroy(args: argparse.Namespace) -> None:  # pragma: no cover
    # TODO get clan folder & hosts from somwhere (maybe ~/.config/clan/$name /)
    # send some kind of kill signal, then remove the folder
    if args.yes:
        print(f"would remove {args.folder}")
    else:
        print(
            "are you really sure? this is non reversible and destructive, add --yes to confirm"
        )


def backup(args: argparse.Namespace) -> None:  # pragma: no cover
    if args.host:
        print(f"would backup {args.host} from clan {args.folder}")
    else:
        print(f"would backup all hosts from clan {args.folder}")


def git(args: argparse.Namespace) -> None:  # pragma: no cover
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

    parser_edit = subparser.add_parser("edit", help="edit a clan")
    parser_edit.set_defaults(func=edit)

    parser_rebuild = subparser.add_parser(
        "rebuild", help="build configuration of a clan and push it to the target"
    )
    parser_rebuild.add_argument(
        "--host", help="specify single host to rebuild", default=None
    )
    parser_rebuild.set_defaults(func=rebuild)

    parser_destroy = subparser.add_parser(
        "destroy", help="destroy a clan, including all the machines"
    )
    parser_destroy.add_argument(
        "--yes", help="specify single host to rebuild", action="store_true"
    )
    parser_destroy.set_defaults(func=destroy)

    parser_backup = subparser.add_parser(
        "backup",
        help="backup all the state of all machines in a clan or just a single one",
    )
    parser_backup.add_argument(
        "--host", help="specify single host to rebuild", default=None
    )
    parser_backup.set_defaults(func=backup)

    parser_git = subparser.add_parser("git", help="control the clan repo via git")
    parser_git.add_argument("git_args", nargs="*")
    parser_git.set_defaults(func=git)
