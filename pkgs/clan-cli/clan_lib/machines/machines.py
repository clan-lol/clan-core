import importlib
import json
import logging
import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from clan_cli.facts import public_modules as facts_public_modules
from clan_cli.facts import secret_modules as facts_secret_modules
from clan_cli.ssh.host_key import HostKeyCheck
from clan_cli.vars._types import StoreBase

from clan_lib.api import API
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import get_machine
from clan_lib.nix import nix_config, nix_test_store
from clan_lib.nix_models.clan import InventoryMachine
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clan_cli.vars.generate import Generator


@dataclass(frozen=True)
class Machine:
    name: str
    flake: Flake

    nix_options: list[str] = field(default_factory=list)
    private_key: Path | None = None
    host_key_check: HostKeyCheck = HostKeyCheck.STRICT

    def get_inv_machine(self) -> "InventoryMachine":
        return get_machine(self.flake, self.name)

    def get_id(self) -> str:
        return f"{self.flake}#{self.name}"

    def flush_caches(self) -> None:
        self.flake.invalidate_cache()

    def __str__(self) -> str:
        return f"Machine(name={self.name}, flake={self.flake})"

    def __repr__(self) -> str:
        return str(self)

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        kwargs.update({"extra": {"command_prefix": self.name}})
        log.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        kwargs.update({"extra": {"command_prefix": self.name}})
        log.info(msg, *args, **kwargs)

    def warn(self, msg: str, *args: Any, **kwargs: Any) -> None:
        kwargs.update({"extra": {"command_prefix": self.name}})
        log.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        kwargs.update({"extra": {"command_prefix": self.name}})
        log.error(msg, *args, **kwargs)

    @property
    # `class` is a keyword, `_class` triggers `SLF001` so we use a sunder name
    def _class_(self) -> str:
        try:
            return self.flake.select(
                f'clanInternals.inventoryClass.inventory.machines."{self.name}".machineClass'
            )
        except ClanCmdError as e:
            if re.search(f"error: attribute '{self.name}' missing", e.cmd.stderr):
                return "nixos"
            raise

    @property
    def system(self) -> str:
        return self.flake.select(
            f'{self._class_}Configurations."{self.name}".pkgs.hostPlatform.system'
        )

    @property
    def deployment(self) -> dict:
        deployment = json.loads(
            self.build_nix("config.system.clan.deployment.file").read_text()
        )
        return deployment

    @cached_property
    def secret_facts_store(self) -> facts_secret_modules.SecretStoreBase:
        module = importlib.import_module(self.deployment["facts"]["secretModule"])
        return module.SecretStore(machine=self)

    @cached_property
    def public_facts_store(self) -> facts_public_modules.FactStoreBase:
        module = importlib.import_module(self.deployment["facts"]["publicModule"])
        return module.FactStore(machine=self)

    @cached_property
    def secret_vars_store(self) -> StoreBase:
        module = importlib.import_module(self.deployment["vars"]["secretModule"])
        return module.SecretStore(machine=self)

    @cached_property
    def public_vars_store(self) -> StoreBase:
        module = importlib.import_module(self.deployment["vars"]["publicModule"])
        return module.FactStore(machine=self)

    @property
    def facts_data(self) -> dict[str, dict[str, Any]]:
        if self.deployment["facts"]["services"]:
            return self.deployment["facts"]["services"]
        return {}

    def vars_generators(self) -> list["Generator"]:
        from clan_cli.vars.generate import Generator

        clan_vars = self.deployment.get("vars")
        if clan_vars is None:
            return []
        generators: dict[str, Any] = clan_vars.get("generators")
        if generators is None:
            return []
        _generators = [Generator.from_json(gen) for gen in generators.values()]
        for gen in _generators:
            gen.machine(self)

        return _generators

    @property
    def secrets_upload_directory(self) -> str:
        return self.deployment["facts"]["secretUploadDirectory"]

    @property
    def flake_dir(self) -> Path:
        return self.flake.path

    def target_host(self) -> Remote:
        remote = get_host(self.name, self.flake, field="targetHost")
        if remote is None:
            msg = f"'targetHost' is not set for machine '{self.name}'"
            raise ClanError(
                msg,
                description="See https://docs.clan.lol/guides/getting-started/deploy/#setting-the-target-host for more information.",
            )
        data = remote.data
        return Remote(
            address=data.address,
            user=data.user,
            command_prefix=data.command_prefix,
            port=data.port,
            private_key=self.private_key,
            password=data.password,
            forward_agent=data.forward_agent,
            host_key_check=self.host_key_check,
            verbose_ssh=data.verbose_ssh,
            ssh_options=data.ssh_options,
            tor_socks=data.tor_socks,
        )

    def build_host(self) -> Remote | None:
        """
        The host where the machine is built and deployed from.
        Can be the same as the target host.
        """
        remote = get_host(self.name, self.flake, field="buildHost")

        if remote:
            data = remote.data
            return Remote(
                address=data.address,
                user=data.user,
                command_prefix=data.command_prefix,
                port=data.port,
                private_key=self.private_key,
                password=data.password,
                forward_agent=data.forward_agent,
                host_key_check=self.host_key_check,
                verbose_ssh=data.verbose_ssh,
                ssh_options=data.ssh_options,
                tor_socks=data.tor_socks,
            )

        return None

    def nix(
        self,
        attr: str,
        nix_options: list[str] | None = None,
    ) -> Any:
        """
        Build the machine and return the path to the result
        accepts a secret store and a facts store # TODO
        """
        if nix_options is None:
            nix_options = []

        config = nix_config()
        system = config["system"]

        return self.flake.select(
            f'clanInternals.machines."{system}"."{self.name}".{attr}',
            nix_options=nix_options,
        )

    def eval_nix(
        self,
        attr: str,
        extra_config: None | dict = None,
        nix_options: list[str] | None = None,
    ) -> Any:
        """
        eval a nix attribute of the machine
        @attr: the attribute to get
        """

        if extra_config:
            log.warning("extra_config in eval_nix is no longer supported")

        if nix_options is None:
            nix_options = []

        return self.nix(attr, nix_options)

    def build_nix(
        self,
        attr: str,
        extra_config: None | dict = None,
        nix_options: list[str] | None = None,
    ) -> Path:
        """
        build a nix attribute of the machine
        @attr: the attribute to get
        """

        if extra_config:
            log.warning("extra_config in build_nix is no longer supported")

        if nix_options is None:
            nix_options = []

        output = self.nix(attr, nix_options)
        output = Path(output)
        if tmp_store := nix_test_store():
            output = tmp_store.joinpath(*output.parts[1:])
        assert output.exists(), f"The output {output} doesn't exist"
        if isinstance(output, Path):
            return output
        msg = "build_nix returned not a Path"
        raise ClanError(msg)


@dataclass(frozen=True)
class RemoteSource:
    data: Remote
    source: Literal["inventory", "nix_machine"]


@API.register
def get_host(
    name: str, flake: Flake, field: Literal["targetHost", "buildHost"]
) -> RemoteSource | None:
    """
    Get the build or target host for a machine.
    """
    machine = Machine(name=name, flake=flake)
    inv_machine = machine.get_inv_machine()

    source: Literal["inventory", "nix_machine"] = "inventory"
    host_str = inv_machine.get("deploy", {}).get(field)

    if host_str is None:
        machine.info(
            f"'{field}' is not set in inventory, falling back to slow Nix config"
        )
        host_str = machine.eval_nix(f'config.clan.core.networking."{field}"')
        source = "nix_machine"

    if not host_str:
        return None

    return RemoteSource(
        data=Remote.from_deployment_address(
            machine_name=machine.name,
            address=host_str,
            host_key_check=machine.host_key_check,
            private_key=machine.private_key,
        ),
        source=source,
    )
