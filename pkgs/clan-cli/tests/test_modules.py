import json
from typing import TYPE_CHECKING

import pytest
from fixtures_flakes import FlakeForTest

from clan_cli.api.modules import list_modules, update_module_instance
from clan_cli.clan_uri import FlakeId
from clan_cli.inventory import Machine, Role, Service, ServiceMeta
from clan_cli.machines.create import create_machine
from clan_cli.nix import nix_eval, run_no_stdout

if TYPE_CHECKING:
    from age_keys import KeyPair

from helpers.cli import Cli

from clan_cli.machines.facts import machine_get_fact


@pytest.mark.with_core
def test_list_modules(test_flake_with_core: FlakeForTest) -> None:
    base_path = test_flake_with_core.path
    modules_info = list_modules(base_path)

    assert len(modules_info.items()) > 1
    # Random test for those two modules
    assert "borgbackup" in modules_info.keys()
    assert "syncthing" in modules_info.keys()


@pytest.mark.impure
def test_add_module_to_inventory(
    monkeypatch: pytest.MonkeyPatch,
    test_flake_with_core: FlakeForTest,
    age_keys: list["KeyPair"],
) -> None:
    base_path = test_flake_with_core.path
    monkeypatch.chdir(test_flake_with_core.path)
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)

    cli = Cli()
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "user1",
            age_keys[0].pubkey,
        ]
    )
    create_machine(
        FlakeId(base_path), Machine(name="machine1", tags=[], system="x86_64-linux")
    )
    update_module_instance(
        base_path,
        "borgbackup",
        "borgbackup1",
        Service(
            meta=ServiceMeta(name="borgbackup"),
            roles={
                "client": Role(machines=["machine1"]),
                "server": Role(machines=["machine1"]),
            },
        ),
    )

    cmd = ["facts", "generate", "--flake", str(test_flake_with_core.path), "machine1"]
    cli.run(cmd)

    ssh_key = machine_get_fact(base_path, "machine1", "borgbackup.ssh.pub")

    cmd = nix_eval(
        [
            f"{base_path}#nixosConfigurations.machine1.config.services.borgbackup.repos",
            "--json",
        ]
    )
    proc = run_no_stdout(cmd)
    res = json.loads(proc.stdout.strip())

    assert res["machine1"]["authorizedKeys"] == [ssh_key]
