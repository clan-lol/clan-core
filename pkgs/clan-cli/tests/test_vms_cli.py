import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest, generate_flake
from root import CLAN_CORE

from clan_cli.dirs import vm_state_dir

if TYPE_CHECKING:
    from age_keys import KeyPair

no_kvm = not os.path.exists("/dev/kvm")


@pytest.mark.impure
def test_inspect(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
    cli.run(["--flake", str(test_flake_with_core.path), "vms", "inspect", "vm1"])
    out = capsys.readouterr()  # empty the buffer
    assert "Cores" in out.out


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_run(
    monkeypatch: pytest.MonkeyPatch,
    test_flake_with_core: FlakeForTest,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.chdir(test_flake_with_core.path)
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    cli = Cli()
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "user1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(["vms", "run", "vm1"])


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_vm_persistence(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "new-clan",
        substitutions=dict(
            __CHANGE_ME__="_test_vm_persistence",
        ),
        machine_configs=dict(
            my_machine=dict(
                clanCore=dict(state=dict(my_state=dict(folders=["/var/my-state"]))),
                systemd=dict(
                    services=dict(
                        poweroff=dict(
                            description="Poweroff the machine",
                            wantedBy=["multi-user.target"],
                            after=["my-state.service"],
                            script="""
                        echo "Powering off the machine"
                        poweroff
                        """,
                        ),
                        my_state=dict(
                            description="Create a file in the state folder",
                            wantedBy=["multi-user.target"],
                            script="""
                        echo "Creating a file in the state folder"
                        echo "dream2nix" > /var/my-state/test
                        """,
                            serviceConfig=dict(Type="oneshot"),
                        ),
                    )
                ),
                clan=dict(virtualisation=dict(graphics=False)),
                users=dict(users=dict(root=dict(password="root"))),
            )
        ),
    )
    monkeypatch.chdir(flake.path)
    cli = Cli()
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "user1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(["vms", "run", "my_machine"])
    test_file = (
        vm_state_dir("_test_vm_persistence", str(flake.path), "my_machine")
        / "var"
        / "my-state"
        / "test"
    )
    assert test_file.exists()
    assert test_file.read_text() == "dream2nix\n"
