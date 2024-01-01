# !/usr/bin/env python3
import argparse
import copy
import datetime

from ..locked_open import write_history_file
from ..nix import nix_metadata
from .add import HistoryEntry, list_history


def update_history() -> list[HistoryEntry]:
    logs = list_history()

    new_logs = []
    for entry in logs:
        new_entry = copy.deepcopy(entry)

        meta = nix_metadata(entry.flake.flake_url)
        new_hash = meta["locked"]["narHash"]
        if new_hash != entry.flake.nar_hash:
            print(
                f"Updating {entry.flake.flake_url} from {entry.flake.nar_hash} to {new_hash}"
            )
            new_entry.last_used = datetime.datetime.now().isoformat()
            new_entry.flake.nar_hash = new_hash

        # TODO: Delete stale entries
        new_logs.append(new_entry)

    write_history_file(new_logs)
    return new_logs


def add_update_command(args: argparse.Namespace) -> None:
    update_history()


# takes a (sub)parser and configures it
def register_update_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=add_update_command)
