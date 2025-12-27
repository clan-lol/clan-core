import importlib
import logging
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Literal

from clan_lib.api import API
from clan_lib.flake import ClanSelectError, Flake
from clan_lib.nix_models.clan import InventoryMachine
from clan_lib.ssh.remote import Remote
from clan_lib.vars._types import StoreBase

log = logging.getLogger(__name__)


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
        from clan_lib.machines.actions import get_machine  # noqa: PLC0415

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
                f'clanInternals.inventoryClass.inventory.machines."{self.name}".machineClass',
            )
        except ClanSelectError:
            return "nixos"

    @property
    def system(self) -> str:
        return self.flake.select(
            f'{self._class_}Configurations."{self.name}".pkgs.stdenv.hostPlatform.system',
        )

    @cached_property
    def secret_vars_store(self) -> StoreBase:
        from clan_cli.vars.secret_modules import password_store  # noqa: PLC0415

        secret_module = self.select("config.clan.core.vars.settings.secretModule")
        module = importlib.import_module(secret_module)
        store = module.SecretStore(flake=self.flake)
        if isinstance(store, password_store.SecretStore):
            store.init_pass_command(machine=self.name)
        return store

    @cached_property
    def public_vars_store(self) -> StoreBase:
        public_module = self.select("config.clan.core.vars.settings.publicModule")
        module = importlib.import_module(public_module)
        return module.VarsStore(flake=self.flake)

    @property
    def flake_dir(self) -> Path:
        return self.flake.path

    def target_host(self) -> Remote:
        from clan_lib.network.network import get_best_remote  # noqa: PLC0415

        with get_best_remote(self) as remote:
            return remote

    def build_host(self) -> Remote | None:
        """The host where the machine is built and deployed from.
        Can be the same as the target host.
        """
        remote = get_machine_host(self.name, self.flake, field="buildHost")

        if remote:
            return remote.data

        return None

    def select(
        self,
        attr: str,
    ) -> Any:
        """Select a nix attribute of the machine
        @attr: the attribute to get
        """
        return self.flake.select_machine(self.name, attr)


@dataclass(frozen=True)
class RemoteSource:
    data: Remote
    source: Literal["inventory", "machine"]


@API.register
def get_machine_host(
    name: str,
    flake: Flake,
    field: Literal["targetHost", "buildHost"],
) -> RemoteSource | None:
    """Get the build or target host for a machine."""
    machine = Machine(name=name, flake=flake)
    inv_machine = machine.get_inv_machine()

    source: Literal["inventory", "machine"] = "inventory"
    host_str = inv_machine.get("deploy", {}).get(field)

    if host_str is None:
        machine.debug(
            f"`inventory.machines.{machine.name}.deploy.{field}` is not set — falling back to `clan.core.networking.{field}`. See: https://docs.clan.lol/guides/networking/networking/",
        )

        host_str = machine.select(f'config.clan.core.networking."{field}"')
        source = "machine"

    if not host_str:
        return None

    return RemoteSource(
        data=Remote.from_ssh_uri(machine_name=machine.name, address=host_str),
        source=source,
    )
