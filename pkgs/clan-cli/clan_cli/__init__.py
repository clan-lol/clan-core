import argparse
import sys
from types import ModuleType
from typing import Optional

from . import admin, machines, secrets, webui

# from . import admin, config, secrets, update, webui
from .errors import ClanError
from .ssh import cli as ssh_cli

argcomplete: Optional[ModuleType] = None
try:
    import argcomplete  # type: ignore[no-redef]
except ImportError:
    pass


# this will be the entrypoint under /bin/clan (see pyproject.toml config)
def main() -> None:
    parser = argparse.ArgumentParser(description="cLAN tool")
    subparsers = parser.add_subparsers()

    parser_admin = subparsers.add_parser("admin", help="administrate a clan")
    admin.register_parser(parser_admin)

    # DISABLED: this currently crashes if a flake does not define .#clanOptions
    # parser_config = subparsers.add_parser("config", help="set nixos configuration")
    # config.register_parser(parser_config)

    parser_ssh = subparsers.add_parser("ssh", help="ssh to a remote machine")
    ssh_cli.register_parser(parser_ssh)

    parser_secrets = subparsers.add_parser("secrets", help="manage secrets")
    secrets.register_parser(parser_secrets)

    parser_machine = subparsers.add_parser(
        "machines", help="Manage machines and their configuration"
    )
    machines.register_parser(parser_machine)

    parser_webui = subparsers.add_parser("webui", help="start webui")
    webui.register_parser(parser_webui)

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
