import argparse
import logging
from typing import TYPE_CHECKING

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.errors import ClanError
from clan_lib.flake import Flake, require_flake
from clan_lib.machines.machines import Machine

if TYPE_CHECKING:
    from .generate import Var

log = logging.getLogger(__name__)


class VarStatus:
    def __init__(
        self,
        missing_secret_vars: list["Var"],
        missing_public_vars: list["Var"],
        unfixed_secret_vars: list["Var"],
        invalid_generators: list[str],
    ) -> None:
        self.missing_secret_vars = missing_secret_vars
        self.missing_public_vars = missing_public_vars
        self.unfixed_secret_vars = unfixed_secret_vars
        self.invalid_generators = invalid_generators


def vars_status(
    machine_name: str, flake: Flake, generator_name: None | str = None
) -> VarStatus:
    machine = Machine(name=machine_name, flake=flake)
    missing_secret_vars = []
    missing_public_vars = []
    # signals if a var needs to be updated (eg. needs re-encryption due to new users added)
    unfixed_secret_vars = []
    invalid_generators = []
    from clan_cli.vars.generate import Generator

    generators = Generator.get_machine_generators(machine.name, machine.flake)
    if generator_name:
        for generator in generators:
            if generator_name == generator.name:
                generators = [generator]
                break
        else:
            err_msg = (
                f"Generator '{generator_name}' not found in machine {machine.name}"
            )
            raise ClanError(err_msg)

    for generator in generators:
        for file in generator.files:
            file.store(
                machine.secret_vars_store if file.secret else machine.public_vars_store
            )
            file.generator(generator)

            if file.secret:
                if not machine.secret_vars_store.exists(generator, file.name):
                    machine.info(
                        f"Secret var '{file.name}' for service '{generator.name}' in machine {machine.name} is missing."
                    )
                    missing_secret_vars.append(file)
                else:
                    msg = machine.secret_vars_store.health_check(
                        machine=machine.name,
                        generator=generator,
                        file_name=file.name,
                    )
                    if msg:
                        machine.info(
                            f"Secret var '{file.name}' for service '{generator.name}' in machine {machine.name} needs update: {msg}"
                        )
                        unfixed_secret_vars.append(file)

            elif not machine.public_vars_store.exists(generator, file.name):
                machine.info(
                    f"Public var '{file.name}' for service '{generator.name}' in machine {machine.name} is missing."
                )
                missing_public_vars.append(file)
        # check if invalidation hash is up to date
        if not (
            machine.secret_vars_store.hash_is_valid(generator)
            and machine.public_vars_store.hash_is_valid(generator)
        ):
            invalid_generators.append(generator.name)
            machine.info(
                f"Generator '{generator.name}' in machine {machine.name} has outdated invalidation hash."
            )
    return VarStatus(
        missing_secret_vars,
        missing_public_vars,
        unfixed_secret_vars,
        invalid_generators,
    )


def check_vars(
    machine_name: str, flake: Flake, generator_name: None | str = None
) -> bool:
    status = vars_status(machine_name, flake, generator_name=generator_name)
    return not (
        status.missing_secret_vars
        or status.missing_public_vars
        or status.unfixed_secret_vars
        or status.invalid_generators
    )


def check_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    ok = check_vars(args.machine, flake, generator_name=args.generator)
    if not ok:
        raise SystemExit(1)


def register_check_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to check secrets for",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--generator",
        "-g",
        help="the generator to check",
    )
    parser.set_defaults(func=check_command)
