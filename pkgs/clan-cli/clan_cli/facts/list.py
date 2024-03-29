import argparse
import importlib
import json
import logging

from ..machines.machines import Machine

log = logging.getLogger(__name__)


# TODO get also secret facts
def get_all_facts(machine: Machine) -> dict:
    public_facts_module = importlib.import_module(machine.public_facts_module)
    public_facts_store = public_facts_module.FactStore(machine=machine)

    # for service in machine.secrets_data:
    #     facts[service] = {}
    #     for fact in machine.secrets_data[service]["facts"]:
    #         fact_content = fact_store.get(service, fact)
    #         if fact_content:
    #             facts[service][fact] = fact_content.decode()
    #         else:
    #             log.error(f"Fact {fact} for service {service} is missing")
    return public_facts_store.get_all()


def get_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    print(json.dumps(get_all_facts(machine), indent=4))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to print facts for",
    )
    parser.set_defaults(func=get_command)
