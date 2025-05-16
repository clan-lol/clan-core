import argparse
import dataclasses
import datetime
import json
import logging
from typing import Any

from clan_cli.clan.inspect import FlakeConfig, inspect_flake
from clan_cli.dirs import user_history_file
from clan_cli.locked_open import read_history_file, write_history_file
from clan_cli.machines.list import list_machines
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake

from clan_vm_manager.clan_uri import ClanURI

log = logging.getLogger(__name__)


@dataclasses.dataclass
class HistoryEntry:
    last_used: str
    flake: FlakeConfig
    settings: dict[str, Any] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_json(cls: type["HistoryEntry"], data: dict[str, Any]) -> "HistoryEntry":
        return cls(
            last_used=data["last_used"],
            flake=FlakeConfig.from_json(data["flake"]),
            settings=data.get("settings", {}),
        )


def _merge_dicts(d1: dict, d2: dict) -> dict:
    # create a new dictionary that copies d1
    merged = dict(d1)
    # iterate over the keys and values of d2
    for key, value in d2.items():
        # if the key is in d1 and both values are dictionaries, merge them recursively
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            merged[key] = _merge_dicts(d1[key], value)
        # otherwise, update the value of the key in the merged dictionary
        else:
            merged[key] = value
    # return the merged dictionary
    return merged


def list_history() -> list[HistoryEntry]:
    logs: list[HistoryEntry] = []
    if not user_history_file().exists():
        return []

    try:
        parsed = read_history_file()
        for i, p in enumerate(parsed.copy()):
            # Everything from the settings dict is merged into the flake dict, and can override existing values
            parsed[i] = _merge_dicts(p, p.get("settings", {}))
        logs = [HistoryEntry.from_json(p) for p in parsed]
    except (json.JSONDecodeError, TypeError) as ex:
        msg = f"History file at {user_history_file()} is corrupted"
        raise ClanError(msg) from ex

    return logs


def new_history_entry(url: str, machine: str) -> HistoryEntry:
    flake = inspect_flake(url, machine)
    return HistoryEntry(
        flake=flake,
        last_used=datetime.datetime.now(tz=datetime.UTC).isoformat(),
    )


def add_all_to_history(uri: ClanURI) -> list[HistoryEntry]:
    history = list_history()
    new_entries: list[HistoryEntry] = []
    for machine in list_machines(Flake(uri.get_url())):
        new_entry = _add_maschine_to_history_list(uri.get_url(), machine, history)
        new_entries.append(new_entry)
    write_history_file(history)
    return new_entries


def add_history(uri: ClanURI) -> HistoryEntry:
    user_history_file().parent.mkdir(parents=True, exist_ok=True)
    history = list_history()
    new_entry = _add_maschine_to_history_list(uri.get_url(), uri.machine_name, history)
    write_history_file(history)
    return new_entry


def _add_maschine_to_history_list(
    uri_path: str, uri_machine: str, entries: list[HistoryEntry]
) -> HistoryEntry:
    for new_entry in entries:
        if (
            new_entry.flake.flake_url == str(uri_path)
            and new_entry.flake.flake_attr == uri_machine
        ):
            new_entry.last_used = datetime.datetime.now(tz=datetime.UTC).isoformat()
            return new_entry

    new_entry = new_history_entry(uri_path, uri_machine)
    entries.append(new_entry)
    return new_entry


def add_history_command(args: argparse.Namespace) -> None:
    if args.all:
        add_all_to_history(args.uri)
    else:
        add_history(args.uri)


def list_history_command(args: argparse.Namespace) -> None:
    res: dict[str, list[HistoryEntry]] = {}
    for history_entry in list_history():
        url = str(history_entry.flake.flake_url)
        if res.get(url) is None:
            res[url] = []
        res[url].append(history_entry)

    for flake_url, entries in res.items():
        print(flake_url)
        for entry in entries:
            d = datetime.datetime.fromisoformat(entry.last_used)
            last_used = d.strftime("%d/%m/%Y %H:%M:%S")
            print(f"  {entry.flake.flake_attr} ({last_used})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="clan history",
        description="Manage clan history",
    )
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    add_parser = subparser.add_parser("add", help="Add a clan flake")
    add_parser.add_argument(
        "uri", type=ClanURI.from_str, help="Path to the flake", default="."
    )
    add_parser.add_argument(
        "--all", help="Add all machines", default=False, action="store_true"
    )
    add_parser.set_defaults(func=add_history_command)
    list_parser = subparser.add_parser("list", help="List recently used flakes")
    list_parser.set_defaults(func=list_history_command)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.func(args)
