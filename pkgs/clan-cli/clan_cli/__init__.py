import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

from . import backups, config, flakes, history, machines, secrets, vms
from .custom_logger import setup_logging
from .dirs import get_clan_flake_toplevel
from .errors import ClanCmdError, ClanError
from .ssh import cli as ssh_cli

log = logging.getLogger(__name__)

argcomplete: ModuleType | None = None
try:
    import argcomplete  # type: ignore[no-redef]
except ImportError:
    pass


class AppendOptionAction(argparse.Action):
    def __init__(self, option_strings: str, dest: str, **kwargs: Any) -> None:
        super().__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        lst = getattr(namespace, self.dest)
        lst.append("--option")
        assert isinstance(values, list), "values must be a list"
        lst.append(values[0])
        lst.append(values[1])


def create_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog, description="cLAN tool")

    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true",
    )

    parser.add_argument(
        "--option",
        help="Nix option to set",
        nargs=2,
        metavar=("name", "value"),
        action=AppendOptionAction,
        default=[],
    )

    def flake_path(arg: str) -> Path:
        flake_dir = Path(arg).resolve()
        if not flake_dir.exists():
            raise argparse.ArgumentTypeError(
                f"flake directory {flake_dir} does not exist"
            )
        if not flake_dir.is_dir():
            raise argparse.ArgumentTypeError(
                f"flake directory {flake_dir} is not a directory"
            )
        return flake_dir

    parser.add_argument(
        "--flake",
        help="path to the flake where the clan resides in",
        default=get_clan_flake_toplevel(),
        type=flake_path,
    )

    subparsers = parser.add_subparsers()

    parser_backups = subparsers.add_parser(
        "backups", help="manage backups of clan machines"
    )
    backups.register_parser(parser_backups)

    parser_flake = subparsers.add_parser(
        "flakes", help="create a clan flake inside the current directory"
    )
    flakes.register_parser(parser_flake)

    parser_config = subparsers.add_parser("config", help="set nixos configuration")
    config.register_parser(parser_config)

    parser_ssh = subparsers.add_parser("ssh", help="ssh to a remote machine")
    ssh_cli.register_parser(parser_ssh)

    parser_secrets = subparsers.add_parser("secrets", help="manage secrets")
    secrets.register_parser(parser_secrets)

    parser_machine = subparsers.add_parser(
        "machines", help="Manage machines and their configuration"
    )
    machines.register_parser(parser_machine)

    parser_vms = subparsers.add_parser("vms", help="manage virtual machines")
    vms.register_parser(parser_vms)

    parser_history = subparsers.add_parser("history", help="manage history")
    history.register_parser(parser_history)

    if argcomplete:
        argcomplete.autocomplete(parser)

    return parser


# this will be the entrypoint under /bin/clan (see pyproject.toml config)
def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    if args.debug:
        setup_logging(logging.DEBUG)
        log.debug("Debug log activated")
    else:
        setup_logging(logging.INFO)

    if not hasattr(args, "func"):
        return

    try:
        args.func(args)
    except ClanError as e:
        if args.debug:
            log.exception(e)
            sys.exit(1)
        if isinstance(e, ClanCmdError):
            if e.cmd.msg:
                print(e.cmd.msg, file=sys.stderr)
            else:
                print(e, file=sys.stderr)
        elif isinstance(e, ClanError):
            print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
