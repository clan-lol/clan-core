import logging
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_test_store

from .check import check_vars
from .prompt import Prompt
from .var import Var

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratorKey:
    """A key uniquely identifying a generator within a clan."""

    machine: str | None
    name: str


@dataclass
class Generator:
    name: str
    files: list[Var] = field(default_factory=list)
    share: bool = False
    prompts: list[Prompt] = field(default_factory=list)
    dependencies: list[GeneratorKey] = field(default_factory=list)

    migrate_fact: str | None = None

    machine: str | None = None
    _flake: "Flake | None" = None

    @property
    def key(self) -> GeneratorKey:
        return GeneratorKey(machine=self.machine, name=self.name)

    def __hash__(self) -> int:
        return hash(self.key)

    @cached_property
    def exists(self) -> bool:
        assert self.machine is not None
        assert self._flake is not None
        return check_vars(self.machine, self._flake, generator_name=self.name)

    @classmethod
    def get_machine_generators(
        cls: type["Generator"],
        machine_name: str,
        flake: "Flake",
        include_previous_values: bool = False,
    ) -> list["Generator"]:
        """
        Get all generators for a machine from the flake.
        Args:
            machine_name (str): The name of the machine.
            flake (Flake): The flake to get the generators from.
        Returns:
            list[Generator]: A list of (unsorted) generators for the machine.
        """
        # Get all generator metadata in one select (safe fields only)
        generators_data = flake.select_machine(
            machine_name,
            "config.clan.core.vars.generators.*.{share,dependencies,migrateFact,prompts}",
        )
        if not generators_data:
            return []

        # Get all file metadata in one select
        files_data = flake.select_machine(
            machine_name,
            "config.clan.core.vars.generators.*.files.*.{secret,deploy,owner,group,mode,neededFor}",
        )

        from clan_lib.machines.machines import Machine

        machine = Machine(name=machine_name, flake=flake)
        pub_store = machine.public_vars_store
        sec_store = machine.secret_vars_store

        generators = []
        for gen_name, gen_data in generators_data.items():
            # Build files from the files_data
            files = []
            gen_files = files_data.get(gen_name, {})
            for file_name, file_data in gen_files.items():
                var = Var(
                    id=f"{gen_name}/{file_name}",
                    name=file_name,
                    secret=file_data["secret"],
                    deploy=file_data["deploy"],
                    owner=file_data["owner"],
                    group=file_data["group"],
                    mode=(
                        file_data["mode"]
                        if isinstance(file_data["mode"], int)
                        else int(file_data["mode"], 8)
                    ),
                    needed_for=file_data["neededFor"],
                    _store=pub_store if not file_data["secret"] else sec_store,
                )
                files.append(var)

            # Build prompts
            prompts = [Prompt.from_nix(p) for p in gen_data.get("prompts", {}).values()]

            generator = cls(
                name=gen_name,
                share=gen_data["share"],
                files=files,
                dependencies=[
                    GeneratorKey(machine=machine_name, name=dep)
                    for dep in gen_data["dependencies"]
                ],
                migrate_fact=gen_data.get("migrateFact"),
                prompts=prompts,
                machine=machine_name,
                _flake=flake,
            )
            generators.append(generator)

        # TODO: This should be done in a non-mutable way.
        if include_previous_values:
            for generator in generators:
                for prompt in generator.prompts:
                    prompt.previous_value = generator.get_previous_value(
                        machine, prompt
                    )

        return generators

    def get_previous_value(
        self,
        machine: "Machine",
        prompt: Prompt,
    ) -> str | None:
        if not prompt.persist:
            return None

        pub_store = machine.public_vars_store
        if pub_store.exists(self, prompt.name):
            return pub_store.get(self, prompt.name).decode()
        sec_store = machine.secret_vars_store
        if sec_store.exists(self, prompt.name):
            return sec_store.get(self, prompt.name).decode()
        return None

    def final_script(self) -> Path:
        assert self.machine is not None
        assert self._flake is not None
        from clan_lib.machines.machines import Machine

        machine = Machine(name=self.machine, flake=self._flake)
        output = Path(
            machine.select(
                f'config.clan.core.vars.generators."{self.name}".finalScript'
            )
        )
        if tmp_store := nix_test_store():
            output = tmp_store.joinpath(*output.parts[1:])
        return output

    def validation(self) -> str | None:
        assert self.machine is not None
        assert self._flake is not None
        from clan_lib.machines.machines import Machine

        machine = Machine(name=self.machine, flake=self._flake)
        return machine.select(
            f'config.clan.core.vars.generators."{self.name}".validationHash'
        )
