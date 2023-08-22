import argparse
import sys

from . import admin, secrets, update
from .errors import ClanError
from .ssh import cli as ssh_cli

argcomplete = None
try:
    import argcomplete
except ImportError:
    pass

config = None
try:
    from . import config
except ImportError:  # jsonschema not installed
    pass


# this will be the entrypoint under /bin/clan (see pyproject.toml config)
def main() -> None:
    parser = argparse.ArgumentParser(description="cLAN tool")
    subparsers = parser.add_subparsers()

    parser_admin = subparsers.add_parser("admin", help="administrate a clan")
    admin.register_parser(parser_admin)

    if config:
        parser_config = subparsers.add_parser("config", help="set nixos configuration")
        config.register_parser(parser_config)

    parser_ssh = subparsers.add_parser("ssh", help="ssh to a remote machine")
    ssh_cli.register_parser(parser_ssh)

    parser_secrets = subparsers.add_parser("secrets", help="manage secrets")
    secrets.register_parser(parser_secrets)

    parser_update = subparsers.add_parser(
        "update", help="update the machines in the clan"
    )
    update.register_parser(parser_update)

    if argcomplete:
        argcomplete.autocomplete(parser)

    if len(sys.argv) == 1:
        parser.print_help()

    args = parser.parse_args()
    if hasattr(args, "func"):
        try:
            args.func(args)
        except ClanError as e:
            print(f"{sys.argv[0]}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
