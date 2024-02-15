import argparse
import importlib
import logging

from ..machines.machines import Machine

log = logging.getLogger(__name__)


def check_facts(machine: Machine) -> bool:
    facts_module = importlib.import_module(machine.facts_module)
    fact_store = facts_module.FactStore(machine=machine)

    existing_facts = fact_store.get_all()
    missing_facts = []
    for service in machine.secrets_data:
        for fact in machine.secrets_data[service]["facts"]:
            if fact not in existing_facts.get(service, {}):
                log.info(f"Fact {fact} for service {service} is missing")
                missing_facts.append((service, fact))

    if missing_facts:
        return False
    return True


def check_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    if check_facts(machine):
        print("All facts are present")


def register_check_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to check facts for",
    )
    parser.set_defaults(func=check_command)
