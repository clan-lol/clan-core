# !/usr/bin/env python3
import argparse

from ..clan_uri import ClanParameters, ClanURI
from ..errors import ClanCmdError
from ..locked_open import write_history_file
from ..nix import nix_metadata
from .add import HistoryEntry, list_history, new_history_entry


def update_history() -> list[HistoryEntry]:
    logs = list_history()

    for entry in logs:
        try:
            meta = nix_metadata(entry.flake.flake_url)
        except ClanCmdError as e:
            print(f"Failed to update {entry.flake.flake_url}: {e}")
            continue

        new_hash = meta["locked"]["narHash"]
        if new_hash != entry.flake.nar_hash:
            print(
                f"Updating {entry.flake.flake_url} from {entry.flake.nar_hash} to {new_hash}"
            )
            uri = ClanURI.from_str(
                url=str(entry.flake.flake_url),
                params=ClanParameters(entry.flake.flake_attr),
            )
            entry = new_history_entry(uri)

    write_history_file(logs)
    return logs


def add_update_command(args: argparse.Namespace) -> None:
    update_history()


# takes a (sub)parser and configures it
def register_update_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=add_update_command)
