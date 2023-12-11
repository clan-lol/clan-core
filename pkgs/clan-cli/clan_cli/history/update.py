# !/usr/bin/env python3
import argparse
import copy
import datetime
import json
from pathlib import Path

from ..dirs import user_history_file
from ..locked_open import locked_open
from .add import EnhancedJSONEncoder, HistoryEntry, get_dir_time, list_history


def update_history() -> list[HistoryEntry]:
    logs = list_history()

    new_logs = []
    for entry in logs:
        new_entry = copy.deepcopy(entry)
        new_time = get_dir_time(Path(entry.path))
        if new_time != entry.dir_datetime:
            print(f"Updating {entry.path} from {entry.dir_datetime} to {new_time}")
            new_entry.dir_datetime = new_time
            new_entry.last_used = datetime.datetime.now().isoformat()
        new_logs.append(new_entry)

    with locked_open(user_history_file(), "w+") as f:
        f.write(json.dumps(new_logs, cls=EnhancedJSONEncoder, indent=4))
        f.truncate()
    return new_logs


def add_update_command(args: argparse.Namespace) -> None:
    update_history()


# takes a (sub)parser and configures it
def register_update_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=add_update_command)
