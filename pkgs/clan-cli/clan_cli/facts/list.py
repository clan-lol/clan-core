import argparse
import json
import logging

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_cli.machines.machines import Machine

log = logging.getLogger(__name__)


def get_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)

    # the raw_facts are bytestrings making them not json serializable
    raw_facts = machine.public_facts_store.get_all()
    facts = {}
    for key in raw_facts["TODO"]:
        facts[key] = raw_facts["TODO"][key].decode("utf8")

    print(json.dumps(facts, indent=4))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to print facts for",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=get_command)
