import subprocess
from pathlib import Path

import pytest
from clan_cli.tests.age_keys import KeyPair
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.vars.public_modules import in_repo as in_repo_mod
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.vars._types import GeneratorId, PerMachine
from clan_lib.vars.get import VarNotFoundError, get_machine_var
from clan_lib.vars.secret_modules import age, sops


def test_cp_command_no_flake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["vars", "cp", "machine1", "machine2", "var1"])


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_cp_command_simple(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Copying a public var to a machine that has not generated it yet yields the same value."""
    flake = flake_with_sops

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    generator = machine1_config["clan"]["core"]["vars"]["generators"]["generator"]
    generator["files"]["my_value"]["secret"] = False
    generator["script"] = 'echo "$RANDOM" > "$out"/my_value'

    # machine 2 is equivalent to machine 1
    flake.machines["machine2"] = machine1_config

    flake.refresh()
    monkeypatch.chdir(flake.path)

    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])
    cli.run(
        [
            "vars",
            "cp",
            "--flake",
            str(flake.path),
            "machine1",
            "machine2",
            "generator/my_value",
        ]
    )

    in_repo_store = in_repo_mod.VarsStore(Flake(str(flake.path)))
    key_m1 = GeneratorId(name="generator", placement=PerMachine("machine1"))
    key_m2 = GeneratorId(name="generator", placement=PerMachine("machine2"))
    assert in_repo_store.get(key_m1, "my_value") == in_repo_store.get(
        key_m2, "my_value"
    )


SECRET_STORES = {"sops": sops.SecretStore, "age": age.SecretStore}


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
@pytest.mark.parametrize(
    ("src_backend", "dest_backend"),
    [("sops", "sops"), ("age", "age"), ("sops", "age"), ("age", "sops")],
)
def test_cp_command_secret(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    age_keys: list[KeyPair],
    src_backend: str,
    dest_backend: str,
) -> None:
    """Copying a secret var stores the source value in the destination machine's secret backend."""
    flake = flake_with_sops
    age_key = age_keys[0]

    for machine, backend in [("machine1", src_backend), ("machine2", dest_backend)]:
        config = flake.machines[machine] = create_test_machine_config()
        clan_vars = config["clan"]["core"]["vars"]
        clan_vars["settings"]["secretStore"] = backend
        generator = clan_vars["generators"]["generator"]
        generator["files"]["my_secret"]["secret"] = True
        generator["script"] = 'echo -n "$RANDOM$RANDOM" > "$out"/my_secret'

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # age backend: recipients for both machines and an identity to decrypt with
    (flake.path / "clan.nix").write_text(
        "{\n"
        f'  vars.settings.recipients.hosts.machine1 = ["{age_key.pubkey}"];\n'
        f'  vars.settings.recipients.hosts.machine2 = ["{age_key.pubkey}"];\n'
        "}\n"
    )
    age_key_file = flake.path / ".age" / "key.txt"
    age_key_file.parent.mkdir()
    age_key_file.write_text(age_key.privkey)
    monkeypatch.setenv("AGE_KEYFILE", str(age_key_file))
    subprocess.run(["git", "add", "."], cwd=flake.path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "setup age backend"], cwd=flake.path, check=True
    )

    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])
    cli.run(
        [
            "vars",
            "cp",
            "--flake",
            str(flake.path),
            "machine1",
            "machine2",
            "generator/my_secret",
        ]
    )

    flake_obj = Flake(str(flake.path))
    src_value = get_machine_var(
        Machine(name="machine1", flake=flake_obj), "generator/my_secret"
    ).value
    dest_value = get_machine_var(
        Machine(name="machine2", flake=flake_obj), "generator/my_secret"
    ).value
    assert dest_value == src_value

    dest_key = GeneratorId(name="generator", placement=PerMachine("machine2"))
    assert SECRET_STORES[dest_backend](flake_obj).exists(dest_key, "my_secret")
    if src_backend != dest_backend:
        assert not SECRET_STORES[src_backend](flake_obj).exists(dest_key, "my_secret")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_cp_command_fails_if_dest_does_not_have_generator(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Copying fails if the destination machine does not have the generator."""
    flake = flake_with_sops

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    generator = machine1_config["clan"]["core"]["vars"]["generators"]["generator"]
    generator["files"]["my_value"]["secret"] = False
    generator["script"] = 'echo "$RANDOM" > "$out"/my_value'

    # machine 2 initialized without the generator
    flake.machines["machine2"] = create_test_machine_config()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])

    with pytest.raises(VarNotFoundError):
        cli.run(
            [
                "vars",
                "cp",
                "--flake",
                str(flake.path),
                "machine1",
                "machine2",
                "generator/my_value",
            ]
        )
