import json
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import clan_cli.clan.create
import pytest
from clan_cli.cmd import RunOpts, run
from clan_cli.dirs import specific_machine_dir
from clan_cli.errors import ClanError
from clan_cli.flake import Flake
from clan_cli.inventory import patch_inventory_with
from clan_cli.machines.create import CreateOptions as ClanCreateOptions
from clan_cli.machines.create import create_machine
from clan_cli.machines.machines import Machine
from clan_cli.nix import nix_command
from clan_cli.secrets.key import generate_key
from clan_cli.secrets.sops import maybe_get_admin_public_key
from clan_cli.secrets.users import add_user
from clan_cli.ssh.host import Host
from clan_cli.ssh.host_key import HostKeyCheck
from clan_cli.vars.generate import generate_vars_for_machine, get_generators_closure

from clan_lib.api.disk import hw_main_disk_options, set_machine_disk_schema
from clan_lib.api.network import check_machine_online
from clan_lib.nix_models.inventory import Machine as InventoryMachine
from clan_lib.nix_models.inventory import MachineDeploy

log = logging.getLogger(__name__)


@dataclass
class InventoryWrapper:
    services: dict[str, Any]
    instances: dict[str, Any]


@dataclass
class InvSSHKeyEntry:
    username: str
    ssh_pubkey_txt: str


@dataclass
class SSHKeyPair:
    private: Path
    public: Path


def create_base_inventory(ssh_keys_pairs: list[SSHKeyPair]) -> InventoryWrapper:
    ssh_keys = [
        InvSSHKeyEntry("nixos-anywhere", ssh_keys_pairs[0].public.read_text()),
    ]
    for num, ssh_key in enumerate(ssh_keys_pairs[1:]):
        ssh_keys.append(InvSSHKeyEntry(f"user_{num}", ssh_key.public.read_text()))

    """Create the base inventory structure."""
    legacy_services: dict[str, Any] = {
        "sshd": {
            "someid": {
                "roles": {
                    "server": {
                        "tags": ["all"],
                        "config": {},
                    }
                }
            }
        },
        "state-version": {
            "someid": {
                "roles": {
                    "default": {
                        "tags": ["all"],
                    }
                }
            }
        },
    }
    instances = {
        "admin-1": {
            "module": {"name": "admin"},
            "roles": {
                "default": {
                    "tags": {"all": {}},
                    "settings": {
                        "allowedKeys": {
                            key.username: key.ssh_pubkey_txt for key in ssh_keys
                        },
                    },
                },
            },
        }
    }

    return InventoryWrapper(services=legacy_services, instances=instances)


# TODO: We need a way to calculate the narHash of the current clan-core
# and substitute it in a pregenerated flake.lock
def fix_flake_inputs(clan_dir: Path, clan_core_dir: Path) -> None:
    flake_nix = clan_dir / "flake.nix"
    assert flake_nix.exists()
    clan_dir_flake = Flake(str(clan_dir))
    clan_dir_flake.invalidate_cache()
    content = flake_nix.read_text()
    content = content.replace(
        "https://git.clan.lol/clan/clan-core/archive/main.tar.gz",
        f"path://{clan_core_dir}",
    )
    flake_nix.write_text(content)

    run(nix_command(["flake", "update"]), RunOpts(cwd=clan_dir))


@pytest.mark.with_core
@pytest.mark.skipif(sys.platform == "darwin", reason="sshd fails to start on darwin")
def test_clan_create_api(
    temporary_home: Path, test_lib_root: Path, clan_core: Path, hosts: list[Host]
) -> None:
    host_ip = hosts[0].host
    host_user = hosts[0].user
    vm_name = "test-clan"
    clan_core_dir_var = str(clan_core)
    priv_key_var = hosts[0].private_key
    ssh_port_var = str(hosts[0].port)

    assert priv_key_var is not None
    private_key = Path(priv_key_var).expanduser()

    assert host_user is not None

    assert private_key.exists()
    assert private_key.is_file()

    public_key = Path(f"{private_key}.pub")
    assert public_key.exists()
    assert public_key.is_file()

    dest_clan_dir = Path("~/new-clan").expanduser()

    # ===== CREATE CLAN ======
    # TODO: We need to generate a lock file for the templates
    clan_cli.clan.create.create_clan(
        clan_cli.clan.create.CreateOptions(
            template_name="minimal", dest=dest_clan_dir, update_clan=False
        )
    )
    assert dest_clan_dir.is_dir()
    assert (dest_clan_dir / "flake.nix").is_file()

    clan_core_dir = Path(clan_core_dir_var)
    # TODO: We need a way to generate the lock file for the templates
    fix_flake_inputs(dest_clan_dir, clan_core_dir)

    # ===== CREATE SOPS KEY ======
    sops_key = maybe_get_admin_public_key()
    if sops_key is None:
        # TODO: In the UI we need a view for this
        sops_key = generate_key()
    else:
        msg = "SOPS key already exists, please remove it before running this test"
        raise ClanError(msg)

    # TODO: This needs to be exposed in the UI and we need a view for this
    add_user(
        dest_clan_dir,
        name="testuser",
        keys=[sops_key],
        force=False,
    )

    # ===== CREATE MACHINE/s ======
    clan_dir_flake = Flake(str(dest_clan_dir))
    machines: list[Machine] = []

    host = Host(user=host_user, host=host_ip, port=int(ssh_port_var))
    # TODO: We need to merge Host and Machine class these duplicate targetHost stuff is a nightmare
    inv_machine = InventoryMachine(
        name=vm_name, deploy=MachineDeploy(targetHost=f"{host.target}:{ssh_port_var}")
    )
    create_machine(
        ClanCreateOptions(
            clan_dir_flake, inv_machine, target_host=f"{host.target}:{ssh_port_var}"
        )
    )

    machine = Machine(
        name=vm_name,
        flake=clan_dir_flake,
        host_key_check=HostKeyCheck.NONE,
        private_key=private_key,
    )
    machines.append(machine)
    assert len(machines) == 1

    # Invalidate cache because of new machine creation
    clan_dir_flake.invalidate_cache()

    result = check_machine_online(machine)
    assert result == "Online", f"Machine {machine.name} is not online"

    ssh_keys = [
        SSHKeyPair(
            private=private_key,
            public=public_key,
        )
    ]

    # ===== CREATE BASE INVENTORY ======
    inventory = create_base_inventory(ssh_keys)
    patch_inventory_with(Flake(str(dest_clan_dir)), "services", inventory.services)

    # Invalidate cache because of new inventory
    clan_dir_flake.invalidate_cache()

    generators = get_generators_closure(machine.name, dest_clan_dir)
    all_prompt_values = {}
    for generator in generators:
        prompt_values = {}
        for prompt in generator.prompts:
            var_id = f"{generator.name}/{prompt.name}"
            if generator.name == "root-password" and prompt.name == "password":
                prompt_values[prompt.name] = "terraform"
            else:
                msg = f"Prompt {var_id} not handled in test, please fix it"
                raise ClanError(msg)
        all_prompt_values[generator.name] = prompt_values

    generate_vars_for_machine(
        machine.name,
        generators=[gen.name for gen in generators],
        base_dir=dest_clan_dir,
        all_prompt_values=all_prompt_values,
    )

    clan_dir_flake.invalidate_cache()

    # ===== Select Disko Config ======
    facter_json = test_lib_root / "assets" / "facter.json"
    assert facter_json.exists(), f"Source facter file not found: {facter_json}"

    dest_dir = specific_machine_dir(machine)
    # specific_machine_dir should create the directory, but ensure it exists just in case
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_facter_path = dest_dir / "facter.json"

    # Copy the file
    shutil.copy(facter_json, dest_facter_path)
    assert dest_facter_path.exists(), (
        f"Failed to copy facter file to {dest_facter_path}"
    )

    # ===== Create Disko Config ======
    facter_path = specific_machine_dir(machine) / "facter.json"
    with facter_path.open("r") as f:
        facter_report = json.load(f)

    disk_devs = hw_main_disk_options(facter_report)

    assert disk_devs is not None

    placeholders = {"mainDisk": disk_devs[0]}
    set_machine_disk_schema(machine, "single-disk", placeholders)
    clan_dir_flake.invalidate_cache()

    # @Qubasa what does this assert check, why does it raise?
    # with pytest.raises(ClanError) as exc_info:
    #     machine.build_nix("config.system.build.toplevel")
    # assert "nixos-system-test-clan" in str(exc_info.value)
