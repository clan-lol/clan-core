import logging
from typing import TYPE_CHECKING

# Scope violation !!! Core cannot depend on CLI
# TODO: Remove this
from clan_cli.vars.secret_modules import sops

from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.machines.machines import Machine

if TYPE_CHECKING:
    from .generator import Var

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

    def text(self) -> str:
        log = ""
        if self.missing_secret_vars:
            log += "Missing secret vars:\n"
            for var in self.missing_secret_vars:
                log += f"  - {var.id}\n"
        if self.missing_public_vars:
            log += "Missing public vars:\n"
            for var in self.missing_public_vars:
                log += f"  - {var.id}\n"
        if self.unfixed_secret_vars:
            log += "Unfixed secret vars:\n"
            for var in self.unfixed_secret_vars:
                log += f"  - {var.id}\n"
        if self.invalid_generators:
            log += "Invalid generators (outdated invalidation hash):\n"
            for gen in self.invalid_generators:
                log += f"  - {gen}\n"
        return log if log else "All vars are present and valid."


def vars_status(
    machine_name: str,
    flake: Flake,
    generator_name: None | str = None,
) -> VarStatus:
    from .generator import Generator  # noqa: PLC0415

    machine = Machine(name=machine_name, flake=flake)
    missing_secret_vars = []
    missing_public_vars = []
    # signals if a var needs to be updated (eg. needs re-encryption due to new users added)
    unfixed_secret_vars = []
    invalid_generators = []

    generators = Generator.get_machine_generators([machine.name], machine.flake)
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
                machine.secret_vars_store if file.secret else machine.public_vars_store,
            )
            file.generator(generator)

            if file.secret:
                if not machine.secret_vars_store.exists(generator, file.name):
                    machine.info(
                        f"Secret var '{file.name}' for service '{generator.name}' in machine {machine.name} is missing.",
                    )
                    missing_secret_vars.append(file)
                if (
                    isinstance(machine.secret_vars_store, sops.SecretStore)
                    and generator.share
                    and file.deploy
                    and file.exists
                    and not machine.secret_vars_store.machine_has_access(
                        generator=generator,
                        secret_name=file.name,
                        machine=machine.name,
                    )
                ):
                    msg = (
                        f"Secret var '{generator.name}/{file.name}' is marked for deployment to machine '{machine.name}', but the machine does not have access to it.\n"
                        f"Run 'clan vars generate {machine.name}' to fix this.\n"
                    )
                    machine.info(msg)
                    missing_secret_vars.append(file)

                else:
                    health_msg = machine.secret_vars_store.health_check(
                        machine=machine.name,
                        generators=[generator],
                        file_name=file.name,
                    )
                    if health_msg is not None:
                        machine.info(
                            f"Secret var '{file.name}' for service '{generator.name}' in machine {machine.name} needs update: {health_msg}",
                        )
                        unfixed_secret_vars.append(file)

            elif not machine.public_vars_store.exists(generator, file.name):
                machine.info(
                    f"Public var '{file.name}' for service '{generator.name}' in machine {machine.name} is missing.",
                )
                missing_public_vars.append(file)
        # check if invalidation hash is up to date
        if not (
            machine.secret_vars_store.hash_is_valid(generator)
            and machine.public_vars_store.hash_is_valid(generator)
        ):
            invalid_generators.append(generator.name)
            machine.info(
                f"Generator '{generator.name}' in machine {machine.name} has outdated invalidation hash.",
            )
    return VarStatus(
        missing_secret_vars,
        missing_public_vars,
        unfixed_secret_vars,
        invalid_generators,
    )


def check_vars(
    machine_name: str,
    flake: Flake,
    generator_name: None | str = None,
) -> bool:
    status = vars_status(machine_name, flake, generator_name=generator_name)
    log.info(f"Check results for machine '{machine_name}': \n{status.text()}")
    return not (
        status.missing_secret_vars
        or status.missing_public_vars
        or status.unfixed_secret_vars
        or status.invalid_generators
    )
