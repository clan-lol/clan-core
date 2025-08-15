import json
import logging
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import clan_cli.clan.create
import pytest
from clan_cli.machines.create import CreateOptions as ClanCreateOptions
from clan_cli.machines.create import create_machine
from clan_cli.secrets.key import generate_key
from clan_cli.secrets.sops import maybe_get_admin_public_keys
from clan_cli.secrets.users import add_user
from clan_cli.vars.generate import get_generators, run_generators

from clan_lib.cmd import RunOpts, run
from clan_lib.dirs import specific_machine_dir
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.flake import ClanSelectError, Flake
from clan_lib.machines.machines import Machine
from clan_lib.network.network import get_network_overview, networks_from_flake
from clan_lib.nix import nix_command
from clan_lib.nix_models.clan import (
    InventoryInstancesType,
    InventoryMachine,
    InventoryServicesType,
    Unknown,
)
from clan_lib.nix_models.clan import InventoryMachineDeploy as MachineDeploy
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path
from clan_lib.services.modules import list_service_modules
from clan_lib.ssh.remote import Remote
from clan_lib.templates.disk import hw_main_disk_options, set_machine_disk_schema

log = logging.getLogger(__name__)


@dataclass
class InventoryWrapper:
    services: InventoryServicesType
    instances: InventoryInstancesType


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
    legacy_services: dict[str, Any] = {}

    instances = InventoryInstancesType(
        {
            "admin-inst": {
                "module": {"name": "admin", "input": "clan-core"},
                "roles": {
                    "default": {
                        "tags": {"all": {}},
                        "settings": cast(
                            Unknown,
                            {
                                "allowedKeys": {
                                    key.username: key.ssh_pubkey_txt for key in ssh_keys
                                }
                            },
                        ),
                    },
                },
            }
        }
    )

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
    temporary_home: Path, test_lib_root: Path, clan_core: Path, hosts: list[Remote]
) -> None:
    host_ip = hosts[0].address
    host_user = hosts[0].user
    vm_name = "test-clan"

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

    dest_clan_dir = Path("~/default").expanduser()

    # ===== CREATE CLAN ======
    # TODO: We need to generate a lock file for the templates
    clan_cli.clan.create.create_clan(
        clan_cli.clan.create.CreateOptions(
            template="minimal", dest=dest_clan_dir, update_clan=False
        )
    )
    assert dest_clan_dir.is_dir()
    assert (dest_clan_dir / "flake.nix").is_file()

    # TODO: We need a way to generate the lock file for the templates
    fix_flake_inputs(dest_clan_dir, clan_core)

    # ===== CREATE SOPS KEY ======
    sops_keys = maybe_get_admin_public_keys()
    if sops_keys is None:
        # TODO: In the UI we need a view for this
        sops_keys = [generate_key()]
    else:
        msg = "SOPS key already exists, please remove it before running this test"
        raise ClanError(msg)

    # TODO: This needs to be exposed in the UI and we need a view for this
    add_user(
        dest_clan_dir,
        name="testuser",
        keys=sops_keys,
        force=False,
    )

    # ===== CREATE MACHINE/s ======
    clan_dir_flake = Flake(str(dest_clan_dir))
    machines: list[Machine] = []

    host = Remote(
        user=host_user, address=host_ip, port=int(ssh_port_var), command_prefix=vm_name
    )
    # TODO: We need to merge Host and Machine class these duplicate targetHost stuff is a nightmare
    inv_machine = InventoryMachine(
        name=vm_name, deploy=MachineDeploy(targetHost=f"{host.target}:{ssh_port_var}")
    )
    create_machine(
        ClanCreateOptions(
            clan_dir_flake, inv_machine, target_host=f"{host.target}:{ssh_port_var}"
        )
    )
    machine = Machine(name=vm_name, flake=clan_dir_flake)
    machines.append(machine)
    assert len(machines) == 1

    # Invalidate cache because of new machine creation
    clan_dir_flake.invalidate_cache()

    target_host = machine.target_host().override(
        private_key=private_key, host_key_check="none"
    )

    target_host.check_machine_ssh_reachable()
    target_host.check_machine_ssh_login()

    ssh_keys = [
        SSHKeyPair(
            private=private_key,
            public=public_key,
        )
    ]

    # ===== CREATE BASE INVENTORY ======
    inventory_conf = create_base_inventory(ssh_keys)
    store = InventoryStore(clan_dir_flake)
    inventory = store.read()

    modules = list_service_modules(clan_dir_flake)
    assert (
        modules["modules"]["clan-core"]["admin"]["manifest"]["name"]
        == "clan-core/admin"
    )

    set_value_by_path(inventory, "services", inventory_conf.services)
    set_value_by_path(inventory, "instances", inventory_conf.instances)
    store.write(
        inventory,
        "base config",
    )

    # Invalidate cache because of new inventory
    clan_dir_flake.invalidate_cache()

    generators = get_generators(machine=machine, full_closure=True)
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

    run_generators(
        machine=machine,
        generators=[gen.name for gen in generators],
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

    # ===== Test that clan network list works ======
    networks = networks_from_flake(clan_dir_flake)
    overview = get_network_overview(networks)
    assert overview is not None

    # In the sandbox, building fails due to network restrictions (can't download dependencies)
    # Outside the sandbox, the build should succeed
    in_sandbox = os.environ.get("IN_NIX_SANDBOX") == "1"

    if in_sandbox:
        # In sandbox: expect build to fail due to network restrictions
        with pytest.raises(ClanSelectError) as select_error:
            Path(machine.select("config.system.build.toplevel"))
        # The error should be a select_error without a failed_attr
        cmd_error = select_error.value.__cause__
        assert cmd_error is not None
        assert isinstance(cmd_error, ClanCmdError)
        assert "nixos-system-test-clan" in str(cmd_error.cmd.stderr)
    else:
        # Outside sandbox: build should succeed
        toplevel_path = Path(machine.select("config.system.build.toplevel"))
        assert toplevel_path.exists()
        # Verify it's a NixOS system by checking for expected content
        assert "nixos-system-test-clan" in str(toplevel_path)
