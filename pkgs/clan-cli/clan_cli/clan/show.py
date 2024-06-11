import argparse
import json
import logging
from pathlib import Path

from clan_cli.api import API
from clan_cli.clan.create import ClanMetaInfo
from clan_cli.errors import ClanCmdError, ClanError

from ..cmd import run_no_stdout
from ..nix import nix_eval

log = logging.getLogger(__name__)


@API.register
def show_clan_meta(uri: str | Path) -> ClanMetaInfo:
    cmd = nix_eval(
        [
            f"{uri}#clanInternals.meta",
            "--json",
        ]
    )
    res = "{}"
    try:
        proc = run_no_stdout(cmd)
        res = proc.stdout.strip()
    except ClanCmdError:
        raise ClanError(
            "Clan might not have meta attributes",
            location=f"show_clan {uri}",
            description="Evaluation failed on clanInternals.meta attribute",
        )

    clan_meta = json.loads(res)
    return ClanMetaInfo(
        name=clan_meta.get("name"),
        description=clan_meta.get("description", None),
        icon=clan_meta.get("icon", None),
    )


def show_command(args: argparse.Namespace) -> None:
    flake_path = Path(args.flake).resolve()
    meta = show_clan_meta(flake_path)

    print(f"Name: {meta.name}")
    print(f"Description: {meta.description or ''}")
    print(f"Icon: {meta.icon or ''}")


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=show_command)
    parser.add_argument(
        "show",
        help="Show",
    )
