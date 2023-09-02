import argparse

from .folders import machine_folder


def create_machine(name: str) -> None:
    folder = machine_folder(name)
    folder.mkdir(parents=True, exist_ok=True)
    # create empty settings.json file inside the folder
    with open(folder / "settings.json", "w") as f:
        f.write("{}")


def create_command(args: argparse.Namespace) -> None:
    create_machine(args.host)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("host", type=str)
    parser.set_defaults(func=create_command)
