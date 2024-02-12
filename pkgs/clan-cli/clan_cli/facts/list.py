import json
import argparse
import importlib
import logging

from ..machines.machines import Machine

log = logging.getLogger(__name__)


def get_all_facts(machine: Machine) -> dict:
    facts_module = importlib.import_module(machine.facts_module)
    fact_store = facts_module.FactStore(machine=machine)

    # for service in machine.secrets_data:
    #     facts[service] = {}
    #     for fact in machine.secrets_data[service]["facts"]:
    #         fact_content = fact_store.get(service, fact)
    #         if fact_content:
    #             facts[service][fact] = fact_content.decode()
    #         else:
    #             log.error(f"Fact {fact} for service {service} is missing")
    return fact_store.get_all()


def get_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    print(json.dumps(get_all_facts(machine), indent=4))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to print facts for",
    )
    parser.set_defaults(func=get_command)
