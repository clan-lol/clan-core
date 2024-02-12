import argparse
import importlib
import logging

from ..machines.machines import Machine

log = logging.getLogger(__name__)


def check_secrets(machine: Machine) -> bool:
    secrets_module = importlib.import_module(machine.secrets_module)
    secret_store = secrets_module.SecretStore(machine=machine)
    facts_module = importlib.import_module(machine.facts_module)
    fact_store = facts_module.FactsStore(machine=machine)

    missing_secrets = []
    missing_facts = []
    for service in machine.secrets_data:
        for secret in machine.secrets_data[service]["secrets"]:
            if not secret_store.exists(service, secret):
                log.info(f"Secret {secret} for service {service} is missing")
                missing_secrets.append((service, secret))

        for fact in machine.secrets_data[service]["facts"].values():
            if not fact_store.exists(service, fact):
                log.info(f"Fact {fact} for service {service} is missing")
                missing_facts.append((service, fact))

    if missing_secrets or missing_facts:
        return False
    return True


def check_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    check_secrets(machine)


def register_check_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to check secrets for",
    )
    parser.set_defaults(func=check_command)
