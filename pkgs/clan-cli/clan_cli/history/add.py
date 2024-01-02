# !/usr/bin/env python3
import argparse
import dataclasses
import datetime
import json
from typing import Any

from clan_cli.flakes.inspect import FlakeConfig, inspect_flake

from ..clan_uri import ClanURI
from ..dirs import user_history_file
from ..errors import ClanError
from ..locked_open import read_history_file, write_history_file


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class HistoryEntry:
    last_used: str
    flake: FlakeConfig
    settings: dict[str, Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.flake, dict):
            self.flake = FlakeConfig(**self.flake)


def merge_dicts(d1: dict, d2: dict) -> dict:
    # create a new dictionary that copies d1
    merged = dict(d1)
    # iterate over the keys and values of d2
    for key, value in d2.items():
        # if the key is in d1 and both values are dictionaries, merge them recursively
        if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
            merged[key] = merge_dicts(d1[key], value)
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
            parsed[i] = merge_dicts(p, p.get("settings", {}))
        logs = [HistoryEntry(**p) for p in parsed]
    except (json.JSONDecodeError, TypeError) as ex:
        raise ClanError(f"History file at {user_history_file()} is corrupted") from ex

    return logs


# TODO: Add all vm entries to history
def add_history(uri: ClanURI) -> list[HistoryEntry]:
    user_history_file().parent.mkdir(parents=True, exist_ok=True)
    logs = list_history()
    found = False
    path = uri.get_internal()
    machine = uri.params.flake_attr

    for entry in logs:
        if entry.flake.flake_url == str(path):
            found = True
            entry.last_used = datetime.datetime.now().isoformat()

    if not found:
        flake = inspect_flake(path, machine)
        flake.flake_url = str(flake.flake_url)
        history = HistoryEntry(
            flake=flake,
            last_used=datetime.datetime.now().isoformat(),
        )
        logs.append(history)

    write_history_file(logs)

    return logs


def add_history_command(args: argparse.Namespace) -> None:
    add_history(args.uri)


# takes a (sub)parser and configures it
def register_add_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "uri", type=ClanURI.from_str, help="Path to the flake", default="."
    )
    parser.set_defaults(func=add_history_command)
