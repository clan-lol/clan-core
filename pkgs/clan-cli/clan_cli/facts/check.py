import argparse
import logging

from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine

from clan_cli.completions import add_dynamic_completer, complete_machines

log = logging.getLogger(__name__)


def check_secrets(machine: Machine, service: None | str = None) -> bool:
    missing_secret_facts = []
    missing_public_facts = []
    services = [service] if service else list(machine.facts_data.keys())
    for svc in services:
        for secret_fact in machine.facts_data[svc]["secret"]:
            if isinstance(secret_fact, str):
                secret_name = secret_fact
            else:
                secret_name = secret_fact["name"]
            if not machine.secret_facts_store.exists(svc, secret_name):
                machine.info(
                    f"Secret fact '{secret_fact}' for service '{svc}' is missing.",
                )
                missing_secret_facts.append((svc, secret_name))

        for public_fact in machine.facts_data[svc]["public"]:
            if not machine.public_facts_store.exists(svc, public_fact):
                machine.info(
                    f"Public fact '{public_fact}' for service '{svc}' is missing.",
                )
                missing_public_facts.append((svc, public_fact))

    machine.debug(f"missing_secret_facts: {missing_secret_facts}")
    machine.debug(f"missing_public_facts: {missing_public_facts}")
    return not (missing_secret_facts or missing_public_facts)


def check_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = Machine(
        name=args.machine,
        flake=flake,
    )
    check_secrets(machine, service=args.service)


def register_check_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to check secrets for",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--service",
        help="the service to check",
    )
    parser.set_defaults(func=check_command)
