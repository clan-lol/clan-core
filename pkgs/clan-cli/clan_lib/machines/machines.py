import importlib
import logging
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from clan_cli.facts import public_modules as facts_public_modules
from clan_cli.facts import secret_modules as facts_secret_modules
from clan_cli.vars._types import StoreBase

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake import ClanSelectError, Flake
from clan_lib.nix_models.clan import InventoryMachine
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class Machine:
    name: str
    flake: Flake

    @classmethod
    def from_inventory(
        cls,
        name: str,
        flake: Flake,
        _inventory_machine: InventoryMachine,
    ) -> "Machine":
        return cls(name=name, flake=flake)

    def get_inv_machine(self) -> "InventoryMachine":
        # Import on demand to avoid circular imports
        from clan_lib.machines.actions import get_machine

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
        except ClanSelectError:
            return "nixos"

    @property
    def system(self) -> str:
        return self.flake.select(
            f'{self._class_}Configurations."{self.name}".pkgs.hostPlatform.system'
        )

    @cached_property
    def secret_facts_store(self) -> facts_secret_modules.SecretStoreBase:
        secret_module = self.select("config.clan.core.facts.secretModule")
        module = importlib.import_module(secret_module)
        return module.SecretStore(machine=self)

    @cached_property
    def public_facts_store(self) -> facts_public_modules.FactStoreBase:
        public_module = self.select("config.clan.core.facts.publicModule")
        module = importlib.import_module(public_module)
        return module.FactStore(machine=self)

    @cached_property
    def secret_vars_store(self) -> StoreBase:
        secret_module = self.select("config.clan.core.vars.settings.secretModule")
        module = importlib.import_module(secret_module)
        return module.SecretStore(flake=self.flake)

    @cached_property
    def public_vars_store(self) -> StoreBase:
        public_module = self.select("config.clan.core.vars.settings.publicModule")
        module = importlib.import_module(public_module)
        return module.FactStore(flake=self.flake)

    @property
    def facts_data(self) -> dict[str, dict[str, Any]]:
        services = self.select("config.clan.core.facts.services")
        if services:
            return services
        return {}

    @property
    def secrets_upload_directory(self) -> str:
        return self.select("config.clan.core.facts.secretUploadDirectory")

    @property
    def flake_dir(self) -> Path:
        return self.flake.path

    def target_host(self) -> Remote:
        remote = get_machine_host(self.name, self.flake, field="targetHost")
        if remote is None:
            msg = f"'targetHost' is not set for machine '{self.name}'"
            raise ClanError(
                msg,
                description="See https://docs.clan.lol/guides/getting-started/update/#setting-the-target-host for more information.",
            )
        data = remote.data
        return data

    def build_host(self) -> Remote | None:
        """
        The host where the machine is built and deployed from.
        Can be the same as the target host.
        """
        remote = get_machine_host(self.name, self.flake, field="buildHost")

        if remote:
            data = remote.data
            return data

        return None

    def select(
        self,
        attr: str,
    ) -> Any:
        """
        Select a nix attribute of the machine
        @attr: the attribute to get
        """
        return self.flake.select_machine(self.name, attr)


@dataclass(frozen=True)
class RemoteSource:
    data: Remote
    source: Literal["inventory", "machine"]


@API.register
def get_machine_host(
    name: str, flake: Flake, field: Literal["targetHost", "buildHost"]
) -> RemoteSource | None:
    """
    Get the build or target host for a machine.
    """
    machine = Machine(name=name, flake=flake)
    inv_machine = machine.get_inv_machine()

    source: Literal["inventory", "machine"] = "inventory"
    host_str = inv_machine.get("deploy", {}).get(field)

    if host_str is None:
        machine.info(
            f"`inventory.machines.{machine.name}.deploy.{field}` is not set — falling back to `clan.core.networking.{field}`. See: https://docs.clan.lol/guides/target-host"
        )

        host_str = machine.select(f'config.clan.core.networking."{field}"')
        source = "machine"

    if not host_str:
        return None

    return RemoteSource(
        data=Remote.from_ssh_uri(machine_name=machine.name, address=host_str),
        source=source,
    )
