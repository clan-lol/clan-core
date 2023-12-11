# !/usr/bin/env python3
import argparse
import dataclasses
import datetime
import json
import os
from pathlib import Path
from typing import Any

from clan_cli.flakes.inspect import FlakeConfig, inspect_flake

from ..dirs import user_history_file
from ..locked_open import locked_open


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class HistoryEntry:
    path: str
    last_used: str
    dir_datetime: str
    flake: FlakeConfig


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


def get_dir_time(path: Path) -> str:
    # Get the last modified dir time in seconds
    dir_mtime = os.path.getmtime(path)
    dir_datetime = datetime.datetime.fromtimestamp(dir_mtime).isoformat()
    return dir_datetime


def add_history(path: Path) -> list[HistoryEntry]:
    user_history_file().parent.mkdir(parents=True, exist_ok=True)
    logs = list_history()

    found = False
    with locked_open(user_history_file(), "w+") as f:
        for entry in logs:
            if entry.path == str(path):
                found = True
                entry.last_used = datetime.datetime.now().isoformat()

        flake = inspect_flake(path, "defaultVM")

        flake.flake_url = str(flake.flake_url)
        dir_datetime = get_dir_time(path)

        history = HistoryEntry(
            flake=flake,
            dir_datetime=dir_datetime,
            path=str(path),
            last_used=datetime.datetime.now().isoformat(),
        )

        if not found:
            logs.append(history)

        f.write(json.dumps(logs, cls=EnhancedJSONEncoder, indent=4))
        f.truncate()

    return logs


def add_history_command(args: argparse.Namespace) -> None:
    add_history(args.path)


# takes a (sub)parser and configures it
def register_add_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path, help="Path to the flake", default=Path("."))
    parser.set_defaults(func=add_history_command)
