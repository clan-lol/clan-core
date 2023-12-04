# !/usr/bin/env python3
import argparse
import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from clan_cli.dirs import user_history_file

from ..locked_open import locked_open


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclass
class HistoryEntry:
    path: str
    last_used: str


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


def push_history(path: Path) -> list[HistoryEntry]:
    user_history_file().parent.mkdir(parents=True, exist_ok=True)
    logs = list_history()

    found = False
    with locked_open(user_history_file(), "w+") as f:
        for entry in logs:
            if entry.path == str(path):
                found = True
                entry.last_used = datetime.now().isoformat()

        if not found:
            logs.append(
                HistoryEntry(path=str(path), last_used=datetime.now().isoformat())
            )

        f.write(json.dumps(logs, cls=EnhancedJSONEncoder))
        f.truncate()

    return logs


def list_history_command(args: argparse.Namespace) -> None:
    for history_entry in list_history():
        print(history_entry.path)


# takes a (sub)parser and configures it
def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_history_command)
