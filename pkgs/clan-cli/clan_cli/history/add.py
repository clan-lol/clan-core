# !/usr/bin/env python3
import argparse
import dataclasses
import datetime
import json
from typing import Any

from clan_cli.flakes.inspect import FlakeConfig, inspect_flake

from ..clan_uri import ClanURI
from ..dirs import user_history_file
from ..locked_open import locked_open


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class HistoryEntry:
    last_used: str
    flake: FlakeConfig

    def __post_init__(self) -> None:
        if isinstance(self.flake, dict):
            self.flake = FlakeConfig(**self.flake)


def list_history() -> list[HistoryEntry]:
    logs: list[HistoryEntry] = []
    if not user_history_file().exists():
        return []

    with locked_open(user_history_file(), "r") as f:
        try:
            content: str = f.read()
            parsed: list[dict] = json.loads(content)
            logs = [HistoryEntry(**p) for p in parsed]
        except json.JSONDecodeError as ex:
            print("Failed to load history. Invalid JSON.")
            print(f"{user_history_file()}: {ex}")

    return logs


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

        if found:
            break

    flake = inspect_flake(path, machine)
    flake.flake_url = str(flake.flake_url)
    history = HistoryEntry(
        flake=flake,
        last_used=datetime.datetime.now().isoformat(),
    )
    logs.append(history)

    with locked_open(user_history_file(), "w+") as f:
        f.write(json.dumps(logs, cls=EnhancedJSONEncoder, indent=4))
        f.truncate()

    return logs


def add_history_command(args: argparse.Namespace) -> None:
    add_history(args.path)


# takes a (sub)parser and configures it
def register_add_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "uri", type=ClanURI, help="Path to the flake", default=ClanURI(".")
    )
    parser.set_defaults(func=add_history_command)
