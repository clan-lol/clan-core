import json
import os
from typing import Any


def default_sunshine_config_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".config", "sunshine")


def default_sunshine_state_file() -> str:
    return os.path.join(default_sunshine_config_dir(), "sunshine_state.json")


def load_state(sunshine_state_path: str) -> dict[str, Any] | None:
    sunshine_state_path = sunshine_state_path or default_sunshine_state_file()
    print(f"Loading sunshine state from {sunshine_state_path}")
    try:
        with open(sunshine_state_path) as file:
            config = file.read()
            return config
    except FileNotFoundError:
        print("Sunshine state file not found.")
        return None


# this needs to be created before sunshine is first run
def init_state(uuid: str, sunshine_state_path: str) -> None:
    print("Initializing sunshine state.")

    data = {}
    data["root"] = {}
    data["root"]["uniqueid"] = uuid
    data["root"]["devices"] = []

    # write the initial bootstrap config file
    write_state(data, sunshine_state_path)


def write_state(data: dict[str, Any], sunshine_state_path: str) -> None:
    sunshine_state_path = sunshine_state_path or default_sunshine_state_file()
    with open(sunshine_state_path, "w") as file:
        json.dump(data, file, indent=4)


# this is used by moonlight-qt
def pseudo_uuid() -> str:
    return "0123456789ABCDEF"


# TODO: finish this function
def add_moonlight_client(certificate: str, sunshine_state_path: str, uuid: str) -> None:
    print("Adding moonlight client to sunshine state.")
    state = load_state(sunshine_state_path)
    if state:
        state = json.loads(state)

        if not state["root"]["devices"]:
            state["root"]["devices"].append(
                {"uniqueid": pseudo_uuid(), "certs": [certificate]}
            )
            write_state(state, sunshine_state_path)
        if certificate not in state["root"]["devices"][0]["certs"]:
            state["root"]["devices"][0]["certs"].append(certificate)
            state["root"]["devices"][0]["uniqueid"] = pseudo_uuid()
            write_state(state, sunshine_state_path)
        else:
            print("Moonlight certificate already added.")
