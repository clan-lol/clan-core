import importlib
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from clan_cli.tests.age_keys import SopsSetup
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.vars.check import check_vars
from clan_cli.vars.get import get_machine_var
from clan_cli.vars.public_modules import in_repo
from clan_cli.vars.secret_modules import password_store, sops
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config, nix_eval, run
from clan_lib.vars._types import GeneratorId, PerMachine, Shared
from clan_lib.vars.generate import (
    run_generators,
)
from clan_lib.vars.generator import (
    Generator,
)
from clan_lib.vars.list import stringify_all_vars
from clan_lib.vars.set import set_var


# Ensure the imports from clan_cli keep working
def test_import_from_cli() -> None:
    # Secret Stores
    importlib.import_module("clan_cli.vars.secret_modules.age")
    importlib.import_module("clan_cli.vars.secret_modules.fs")
    importlib.import_module("clan_cli.vars.secret_modules.password_store")
    importlib.import_module("clan_cli.vars.secret_modules.sops")
    # Public Store
    importlib.import_module("clan_cli.vars.public_modules.in_repo")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_public_and_secret_vars(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test generation of public and secret vars with dependencies.

    Generator dependency graph:

    my_generator (standalone)
        ├── my_value (public)
        ├── my_secret (secret)
        └── value_with_default (public, has default)

    my_shared_generator (shared=True)
        └── my_shared_value (public)
                ↓
    dependent_generator (depends on my_shared_generator)
        └── my_secret (secret, copies from my_shared_value)

    This test verifies:
    - Public and secret vars are stored correctly
    - Shared generators work across dependencies
    - Default values are handled properly
    - Regeneration with --regenerate updates all values
    - Regeneration with --regenerate --generator only updates specified generator
    """
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["files"]["value_with_default"]["secret"] = False
    my_generator["files"]["value_with_default"]["value"]["_type"] = "override"
    my_generator["files"]["value_with_default"]["value"]["priority"] = 1000  # mkDefault
    my_generator["files"]["value_with_default"]["value"]["content"] = "default_value"
    my_generator["script"] = (
        'echo -n public$RANDOM > "$out"/my_value; echo -n secret$RANDOM > "$out"/my_secret; echo -n non-default$RANDOM > "$out"/value_with_default'
    )

    my_shared_generator = config["clan"]["core"]["vars"]["generators"][
        "my_shared_generator"
    ]
    my_shared_generator["share"] = True
    my_shared_generator["files"]["my_shared_value"]["secret"] = False
    my_shared_generator["script"] = 'echo -n shared$RANDOM > "$out"/my_shared_value'

    dependent_generator = config["clan"]["core"]["vars"]["generators"][
        "dependent_generator"
    ]
    dependent_generator["share"] = False
    dependent_generator["files"]["my_secret"]["secret"] = True
    dependent_generator["dependencies"] = ["my_shared_generator"]
    dependent_generator["script"] = (
        'cat "$in"/my_shared_generator/my_shared_value > "$out"/my_secret'
    )

    flake.refresh()
    monkeypatch.chdir(flake.path)

    machine = Machine(name="my_machine", flake=Flake(str(flake.path)))
    assert not check_vars(machine.name, machine.flake)
    vars_text = stringify_all_vars(machine)
    assert "my_generator/my_value: <not set>" in vars_text
    assert "my_generator/my_secret: <not set>" in vars_text
    assert "my_shared_generator/my_shared_value: <not set>" in vars_text
    assert "dependent_generator/my_secret: <not set>" in vars_text

    # ensure evaluating the default value works without generating the value
    value_non_default = run(
        nix_eval(
            [
                f"{flake.path}#nixosConfigurations.my_machine.config.clan.core.vars.generators.my_generator.files.value_with_default.value",
            ],
        ),
    ).stdout.strip()
    assert json.loads(value_non_default) == "default_value"

    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    assert check_vars(machine.name, machine.flake)
    # get last commit message
    commit_message = run(
        ["git", "log", "-6", "--pretty=%B"],
    ).stdout.strip()
    # Example git log:
    # vars: update via generator dependent_generator (machine: my_machine)
    # vars: update via generator my_generator (machine: my_machine)
    # secrets: add machine my_machine
    # secrets: update my_machine-age.key
    # vars: update via generator my_shared_generator (shared)
    # flake: update by flake generator
    assert (
        "vars: update via generator my_generator (machine: my_machine)"
        in commit_message
    )
    assert "vars: update via generator my_shared_generator (shared)" in commit_message
    public_value = get_machine_var(machine, "my_generator/my_value").printable_value
    assert public_value.startswith("public")
    shared_value = get_machine_var(
        machine,
        "my_shared_generator/my_shared_value",
    ).printable_value
    assert shared_value.startswith("shared")
    vars_text = stringify_all_vars(machine)
    flake_obj = Flake(str(flake.path))
    my_generator = Generator(
        key=GeneratorId(
            name="my_generator", placement=PerMachine(machine="my_machine")
        ),
        _flake=flake_obj,
    )
    shared_generator = Generator(
        key=GeneratorId(name="my_shared_generator", placement=Shared()),
        _flake=flake_obj,
    )
    dependent_generator = Generator(
        key=GeneratorId(
            name="dependent_generator", placement=PerMachine(machine="my_machine")
        ),
        _flake=flake_obj,
    )
    in_repo_store = in_repo.VarsStore(flake=flake_obj)
    assert not in_repo_store.exists(my_generator.key, "my_secret")
    sops_store = sops.SecretStore(flake=flake_obj)
    assert sops_store.exists(my_generator.key, "my_secret")
    assert sops_store.get(my_generator.key, "my_secret").decode().startswith("secret")
    assert sops_store.exists(dependent_generator.key, "my_secret")
    secret_value = sops_store.get(dependent_generator.key, "my_secret").decode()
    assert secret_value.startswith("shared")

    assert "my_generator/my_value: public" in vars_text
    assert "my_generator/my_secret" in vars_text
    vars_eval = run(
        nix_eval(
            [
                f"{flake.path}#nixosConfigurations.my_machine.config.clan.core.vars.generators.my_generator.files.my_value.value",
            ],
        ),
    ).stdout.strip()
    assert json.loads(vars_eval).startswith("public")

    value_non_default = run(
        nix_eval(
            [
                f"{flake.path}#nixosConfigurations.my_machine.config.clan.core.vars.generators.my_generator.files.value_with_default.value",
            ],
        ),
    ).stdout.strip()
    assert json.loads(value_non_default).startswith("non-default")

    # test regeneration works
    cli.run(
        ["vars", "generate", "--flake", str(flake.path), "my_machine", "--regenerate"],
    )
    # test regeneration without sandbox
    cli.run(
        [
            "vars",
            "generate",
            "--flake",
            str(flake.path),
            "my_machine",
            "--regenerate",
            "--no-sandbox",
        ],
    )
    # test stuff actually changed after regeneration
    public_value_new = get_machine_var(machine, "my_generator/my_value").printable_value
    assert public_value_new != public_value, "Value should change after regeneration"
    secret_value_new = sops_store.get(dependent_generator.key, "my_secret").decode()
    assert secret_value_new != secret_value, (
        "Secret value should change after regeneration"
    )
    shared_value_new = get_machine_var(
        machine,
        "my_shared_generator/my_shared_value",
    ).printable_value
    assert shared_value != shared_value_new, (
        "Shared value should change after regeneration"
    )
    # test that after regenerating a shared generator, it and its dependents are regenerated
    cli.run(
        [
            "vars",
            "generate",
            "--flake",
            str(flake.path),
            "my_machine",
            "--regenerate",
            "--no-sandbox",
            "--generator",
            "my_shared_generator",
        ],
    )
    # test that the shared generator is regenerated
    shared_value_after_regeneration = get_machine_var(
        machine,
        "my_shared_generator/my_shared_value",
    ).printable_value
    assert shared_value_after_regeneration != shared_value_new, (
        "Shared value should change after regenerating my_shared_generator"
    )
    # test that the dependent generator is also regenerated (because it depends on my_shared_generator)
    secret_value_after_regeneration = sops_store.get(
        dependent_generator.key,
        "my_secret",
    ).decode()
    assert secret_value_after_regeneration != secret_value_new, (
        "Dependent generator's secret should change after regenerating my_shared_generator"
    )
    assert secret_value_after_regeneration == shared_value_after_regeneration, (
        "Dependent generator's secret should match the new shared value"
    )
    # test that my_generator is NOT regenerated (it doesn't depend on my_shared_generator)
    public_value_after_regeneration = get_machine_var(
        machine,
        "my_generator/my_value",
    ).printable_value
    assert public_value_after_regeneration == public_value_new, (
        "my_generator value should NOT change after regenerating only my_shared_generator"
    )

    # test that a dependent is generated on a clean slate even when no --regenerate is given
    # remove all generated vars
    in_repo_store.delete_store("my_machine")
    sops_store.delete(shared_generator.key, "my_shared_value")
    sops_store.delete_store("my_machine")
    cli.run(
        [
            "vars",
            "generate",
            "--flake",
            str(flake.path),
            "my_machine",
            "--generator",
            "my_shared_generator",
        ]
    )
    # check that both my_shared_generator and dependent_generator are generated
    shared_value_clean = get_machine_var(
        machine,
        "my_shared_generator/my_shared_value",
    ).printable_value
    assert shared_value_clean.startswith("shared"), "Shared value should be generated"
    assert sops_store.exists(dependent_generator.key, "my_secret"), (
        "Dependent generator's secret should be generated"
    )
    secret_value_clean = sops_store.get(dependent_generator.key, "my_secret").decode()
    assert secret_value_clean == shared_value_clean, (
        "Dependent generator's secret should match the shared value"
    )


# TODO: it doesn't actually test if the group has access
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_secret_var_sops_with_default_group(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    sops_setup: SopsSetup,
) -> None:
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    config["clan"]["core"]["sops"]["defaultGroups"] = ["my_group"]
    first_generator = config["clan"]["core"]["vars"]["generators"]["first_generator"]
    first_generator["files"]["my_secret"]["secret"] = True
    first_generator["files"]["my_public"]["secret"] = False
    first_generator["script"] = (
        'echo hello > "$out"/my_secret && echo hello > "$out"/my_public'
    )
    second_generator = config["clan"]["core"]["vars"]["generators"]["second_generator"]
    second_generator["files"]["my_secret"]["secret"] = True
    second_generator["files"]["my_public"]["secret"] = False
    second_generator["script"] = (
        'echo hello > "$out"/my_secret && echo hello > "$out"/my_public'
    )
    flake.refresh()
    monkeypatch.chdir(flake.path)
    cli.run(["secrets", "groups", "add-user", "my_group", sops_setup.user])
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    flake_obj = Flake(str(flake.path))
    first_generator = Generator(
        key=GeneratorId(
            name="first_generator", placement=PerMachine(machine="my_machine")
        ),
        _flake=flake_obj,
    )
    second_generator = Generator(
        key=GeneratorId(
            name="second_generator", placement=PerMachine(machine="my_machine")
        ),
        _flake=flake_obj,
    )
    in_repo_store = in_repo.VarsStore(flake=flake_obj)
    assert not in_repo_store.exists(first_generator.key, "my_secret")
    sops_store = sops.SecretStore(flake=flake_obj)
    assert sops_store.exists(first_generator.key, "my_secret")
    assert sops_store.get(first_generator.key, "my_secret").decode() == "hello\n"
    assert sops_store.exists(second_generator.key, "my_secret")
    assert sops_store.get(second_generator.key, "my_secret").decode() == "hello\n"

    # add another user to the group and check if secret gets re-encrypted
    pubkey_user2 = sops_setup.keys[1]
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            "user2",
            pubkey_user2.pubkey,
        ],
    )
    cli.run(["secrets", "groups", "add-user", "my_group", "user2"])
    # check if new user can access the secret
    monkeypatch.setenv("USER", "user2")
    first_generator_with_share = Generator(
        key=GeneratorId(
            name="first_generator", placement=PerMachine(machine="my_machine")
        ),
        _flake=flake_obj,
    )
    second_generator_with_share = Generator(
        key=GeneratorId(
            name="second_generator", placement=PerMachine(machine="my_machine")
        ),
        _flake=flake_obj,
    )
    assert sops_store.user_has_access(
        "user2", first_generator_with_share.key, "my_secret"
    )
    assert sops_store.user_has_access(
        "user2", second_generator_with_share.key, "my_secret"
    )

    # Rotate key of a user
    pubkey_user3 = sops_setup.keys[2]
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            "--force",
            "user2",
            pubkey_user3.pubkey,
        ],
    )
    monkeypatch.setenv("USER", "user2")
    assert sops_store.user_has_access(
        "user2", first_generator_with_share.key, "my_secret"
    )
    assert sops_store.user_has_access(
        "user2", second_generator_with_share.key, "my_secret"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_shared_secret_sops(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    flake = flake_with_sops

    m1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_generator = m1_config["clan"]["core"]["vars"]["generators"][
        "my_shared_generator"
    ]
    shared_generator["share"] = True
    shared_generator["files"]["my_shared_secret"]["secret"] = True
    shared_generator["files"]["no_deploy_secret"]["secret"] = True
    shared_generator["files"]["no_deploy_secret"]["deploy"] = False
    shared_generator["script"] = (
        'echo hello > "$out"/my_shared_secret; echo no_hello > "$out"/no_deploy_secret'
    )
    m2_config = flake.machines["machine2"] = create_test_machine_config()
    m2_config["clan"]["core"]["vars"]["generators"]["my_shared_generator"] = (
        shared_generator.copy()
    )
    # machine 3 should not have the shared secret
    flake.machines["machine3"] = create_test_machine_config()
    flake.refresh()
    monkeypatch.chdir(flake.path)
    machine1 = Machine(name="machine1", flake=Flake(str(flake.path)))
    machine2 = Machine(name="machine2", flake=Flake(str(flake.path)))
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine2"])

    # Get the initial state of the flake directory after generation
    def get_file_mtimes(path: str) -> dict[str, float]:
        """Get modification times of all files in a directory tree."""
        mtimes = {}
        for root, _dirs, files in os.walk(path):
            # Skip .git directory
            if ".git" in root:
                continue
            for file in files:
                filepath = Path(root) / file
                mtimes[str(filepath)] = filepath.stat().st_mtime
        return mtimes

    initial_mtimes = get_file_mtimes(str(flake.path))

    # First check_vars should not write anything
    assert check_vars(machine2.name, machine2.flake), (
        "machine2 has already generated vars, so check_vars should return True\n"
        f"Check result:\n{check_vars(machine2.name, machine2.flake)}"
    )
    # Verify no files were modified
    after_check_mtimes = get_file_mtimes(str(flake.path))
    assert initial_mtimes == after_check_mtimes, (
        "check_vars should not modify any files when vars are already valid"
    )

    # Verify no files were modified
    after_check_mtimes_2 = get_file_mtimes(str(flake.path))
    assert initial_mtimes == after_check_mtimes_2, (
        "check_vars should not modify any files when vars are not valid"
    )

    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])

    # Check that the commit message includes the secret path when adding machine to secret
    commit_messages = run(
        ["git", "log", "-10", "--pretty=%B"],
    ).stdout.strip()
    assert "vars: update via generator my_shared_generator (shared)" in commit_messages

    m1_sops_store = sops.SecretStore(machine1.flake)
    m2_sops_store = sops.SecretStore(machine2.flake)
    # Create generators with machine context for testing
    generator_m1 = Generator(
        key=GeneratorId(name="my_shared_generator", placement=Shared()),
        _flake=machine1.flake,
    )
    generator_m2 = Generator(
        key=GeneratorId(name="my_shared_generator", placement=Shared()),
        _flake=machine2.flake,
    )

    assert m1_sops_store.exists(generator_m1.key, "my_shared_secret")
    assert m1_sops_store.exists(generator_m1.key, "no_deploy_secret")
    assert m2_sops_store.exists(generator_m2.key, "my_shared_secret")
    assert m2_sops_store.exists(generator_m2.key, "no_deploy_secret")
    assert m1_sops_store.machine_has_access(
        generator_m1.key, "my_shared_secret", "machine1"
    )
    assert m2_sops_store.machine_has_access(
        generator_m2.key, "my_shared_secret", "machine2"
    )
    assert not m1_sops_store.machine_has_access(
        generator_m1.key, "no_deploy_secret", "machine1"
    )
    assert not m2_sops_store.machine_has_access(
        generator_m2.key, "no_deploy_secret", "machine2"
    )

    cli.run(["vars", "generate", "--flake", str(flake.path)])
    machine3 = Machine(name="machine3", flake=Flake(str(flake.path)))
    m3_sops_store = sops.SecretStore(machine3.flake)
    generator_m3 = Generator(
        key=GeneratorId(name="my_shared_generator", placement=Shared()),
        _flake=machine3.flake,
    )
    assert not m3_sops_store.machine_has_access(
        generator_m3.key,
        "my_shared_secret",
        "machine3",
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_secret_var_password_store(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    test_root: Path,
) -> None:
    config = flake.machines["my_machine"] = create_test_machine_config()
    clan_vars = config["clan"]["core"]["vars"]
    clan_vars["settings"]["secretStore"] = "password-store"
    # Use pass (GPG-based) for this test
    config["clan"]["core"]["vars"]["password-store"]["passCommand"] = "pass"
    # Create a second secret so that when we delete the first one,
    # we still have the second one to test `delete_store`:
    my_generator = clan_vars["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = 'echo hello > "$out"/my_secret'
    my_generator2 = clan_vars["generators"]["my_generator2"]
    my_generator2["files"]["my_secret2"]["secret"] = True
    my_generator2["script"] = 'echo world > "$out"/my_secret2'
    my_shared_generator = clan_vars["generators"]["my_shared_generator"]
    my_shared_generator["share"] = True
    my_shared_generator["files"]["my_shared_secret"]["secret"] = True
    my_shared_generator["script"] = 'echo hello > "$out"/my_shared_secret'
    flake.refresh()
    monkeypatch.chdir(flake.path)
    gnupghome = flake.path / "gpg"
    shutil.copytree(test_root / "data" / "gnupg-home", gnupghome)
    monkeypatch.setenv("GNUPGHOME", str(gnupghome))

    password_store_dir = flake.path / "pass"
    shutil.copytree(test_root / "data" / "password-store", password_store_dir)
    monkeypatch.setenv("PASSWORD_STORE_DIR", str(password_store_dir))

    # Initialize password store as a git repository

    subprocess.run(["git", "init"], cwd=password_store_dir, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=password_store_dir,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=password_store_dir,
        check=True,
    )

    flake_obj = Flake(str(flake.path))
    machine = Machine(name="my_machine", flake=flake_obj)
    assert not check_vars(machine.name, machine.flake)
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    assert check_vars(machine.name, machine.flake)
    store = password_store.SecretStore(flake=flake_obj)
    store.init_pass_command(machine="my_machine")
    my_generator = Generator(
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
        files=[],
        _flake=flake_obj,
    )
    my_generator_shared = Generator(
        key=GeneratorId(name="my_generator", placement=Shared()),
        files=[],
        _flake=flake_obj,
    )
    my_shared_generator = Generator(
        key=GeneratorId(name="my_shared_generator", placement=Shared()),
        files=[],
        _flake=flake_obj,
    )
    my_shared_generator_not_shared = Generator(
        key=GeneratorId(name="my_shared_generator", placement=PerMachine("my_machine")),
        files=[],
        _flake=flake_obj,
    )
    assert store.exists(my_generator.key, "my_secret")
    assert not store.exists(my_generator_shared.key, "my_secret")
    assert store.exists(my_shared_generator.key, "my_shared_secret")
    assert not store.exists(my_shared_generator_not_shared.key, "my_shared_secret")

    generator = Generator(
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
        files=[],
        _flake=flake_obj,
    )
    assert store.get(generator.key, "my_secret").decode() == "hello\n"
    vars_text = stringify_all_vars(machine)
    assert "my_generator/my_secret" in vars_text

    my_generator = Generator(
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
        files=[],
        _flake=flake_obj,
    )
    var_name = "my_secret"
    store.delete(my_generator.key, var_name)
    assert not store.exists(my_generator.key, var_name)

    store.delete_store("my_machine")
    store.delete_store("my_machine")  # check idempotency
    my_generator2 = Generator(
        key=GeneratorId(name="my_generator2", placement=PerMachine("my_machine")),
        files=[],
        _flake=flake_obj,
    )
    var_name = "my_secret2"
    assert not store.exists(my_generator2.key, var_name)

    # The shared secret should still be there,
    # not sure if we can delete those automatically:
    my_shared_generator = Generator(
        key=GeneratorId(name="my_shared_generator", placement=Shared()),
        files=[],
        _flake=flake_obj,
    )
    var_name = "my_shared_secret"
    assert store.exists(my_shared_generator.key, var_name)


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_secret_for_multiple_machines(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    flake = flake_with_sops

    local_system = nix_config()["system"]

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    machine1_generator = machine1_config["clan"]["core"]["vars"]["generators"][
        "my_generator"
    ]
    machine1_generator["files"]["my_secret"]["secret"] = True
    machine1_generator["files"]["my_value"]["secret"] = False
    machine1_generator["script"] = (
        'echo machine1 > "$out"/my_secret && echo machine1 > "$out"/my_value'
    )
    # Test that we can generate secrets for other platforms
    machine2_config = flake.machines["machine2"] = create_test_machine_config(
        "aarch64-linux" if local_system == "x86_64-linux" else "x86_64-linux"
    )

    machine2_generator = machine2_config["clan"]["core"]["vars"]["generators"][
        "my_generator"
    ]
    machine2_generator["files"]["my_secret"]["secret"] = True
    machine2_generator["files"]["my_value"]["secret"] = False
    machine2_generator["script"] = (
        'echo machine2 > "$out"/my_secret && echo machine2 > "$out"/my_value'
    )
    flake.refresh()
    monkeypatch.chdir(flake.path)
    cli.run(["vars", "generate", "--flake", str(flake.path)])
    # check if public vars have been created correctly
    flake_obj = Flake(str(flake.path))
    in_repo_store1 = in_repo.VarsStore(flake=flake_obj)
    in_repo_store2 = in_repo.VarsStore(flake=flake_obj)

    # Create generators for each machine
    gen1 = Generator(
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=PerMachine("machine1")),
    )
    gen2 = Generator(
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=PerMachine("machine2")),
    )

    assert in_repo_store1.exists(gen1.key, "my_value")
    assert in_repo_store2.exists(gen2.key, "my_value")
    assert in_repo_store1.get(gen1.key, "my_value").decode() == "machine1\n"
    assert in_repo_store2.get(gen2.key, "my_value").decode() == "machine2\n"
    # check if secret vars have been created correctly
    sops_store1 = sops.SecretStore(flake=flake_obj)
    sops_store2 = sops.SecretStore(flake=flake_obj)
    assert sops_store1.exists(gen1.key, "my_secret")
    assert sops_store2.exists(gen2.key, "my_secret")
    assert sops_store1.get(gen1.key, "my_secret").decode() == "machine1\n"
    assert sops_store2.get(gen2.key, "my_secret").decode() == "machine2\n"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_stdout_of_generate(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    caplog: pytest.LogCaptureFixture,
) -> None:
    flake_ = flake_with_sops

    config = flake_.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = 'echo -n hello > "$out"/my_value'
    my_secret_generator = config["clan"]["core"]["vars"]["generators"][
        "my_secret_generator"
    ]
    my_secret_generator["files"]["my_secret"]["secret"] = True
    my_secret_generator["script"] = 'echo -n hello > "$out"/my_secret'
    flake_.refresh()
    monkeypatch.chdir(flake_.path)
    flake = Flake(str(flake_.path))
    # with capture_output as output:
    with caplog.at_level(logging.INFO):
        run_generators(
            machines=[Machine(name="my_machine", flake=flake)],
            generators=["my_generator"],
        )

    assert "Updated var my_generator/my_value for machines: my_machine" in caplog.text
    assert "old: <not set>" in caplog.text
    assert "new: hello" in caplog.text
    caplog.clear()

    set_var("my_machine", "my_generator/my_value", b"world", flake)
    with caplog.at_level(logging.INFO):
        run_generators(
            machines=[Machine(name="my_machine", flake=flake)],
            generators=["my_generator"],
        )
    assert "Updated var my_generator/my_value for machines: my_machine" in caplog.text
    assert "old: world" in caplog.text
    assert "new: hello" in caplog.text
    caplog.clear()
    # check the output when nothing gets regenerated
    with caplog.at_level(logging.INFO):
        run_generators(
            machines=[Machine(name="my_machine", flake=flake)],
            generators=["my_generator"],
        )
    assert "Updated var" not in caplog.text
    assert "hello" in caplog.text
    caplog.clear()
    with caplog.at_level(logging.INFO):
        run_generators(
            machines=[Machine(name="my_machine", flake=flake)],
            generators=["my_secret_generator"],
        )
    assert (
        "Updated secret var my_secret_generator/my_secret for machines: my_machine"
        in caplog.text
    )
    assert "hello" not in caplog.text
    caplog.clear()
    set_var(
        "my_machine",
        "my_secret_generator/my_secret",
        b"world",
        Flake(str(flake.path)),
    )
    with caplog.at_level(logging.INFO):
        run_generators(
            machines=[Machine(name="my_machine", flake=flake)],
            generators=["my_secret_generator"],
        )
    assert "Updated secret var my_secret_generator/my_secret" in caplog.text
    assert "world" not in caplog.text
    assert "hello" not in caplog.text
    caplog.clear()


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_create_sops_age_secrets(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    monkeypatch.chdir(flake.path)
    cli.run(["vars", "keygen", "--flake", str(flake.path), "--user", "user"])
    # check public key exists
    assert (flake.path / "sops" / "users" / "user").is_dir()
    # check private key exists
    assert (flake.temporary_home / ".config" / "sops" / "age" / "keys.txt").is_file()
    # it should still work, even if the keys already exist
    shutil.rmtree(flake.path / "sops" / "users" / "user")
    cli.run(["vars", "keygen", "--flake", str(flake.path), "--user", "user"])
    # check public key exists
    assert (flake.path / "sops" / "users" / "user").is_dir()


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_sops_fix_commits_all_changes(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    sops_setup: SopsSetup,
) -> None:
    """Test that 'clan vars fix' commits all changes (group symlinks, re-encrypted secrets).

    Generate secrets WITHOUT a default group, then add the group to defaultGroups.
    This forces fix() to create new group symlinks and re-encrypt, exercising the
    code paths where return values from allow_member/update_keys must be committed.
    """
    flake = flake_with_sops

    # Step 1: Create machine with secret but NO defaultGroups
    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = 'echo -n secret_value > "$out"/my_secret'

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Step 2: Create group with admin user (exists in sops/ but not linked to any secret)
    cli.run(["secrets", "groups", "add-user", "my_group", sops_setup.user])

    # Step 3: Generate secrets (no defaultGroups, so group is NOT linked to the secret)
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])

    # Step 4: Now add the group to defaultGroups and refresh config
    config["clan"]["core"]["sops"]["defaultGroups"] = ["my_group"]
    flake.refresh()

    # Step 5: Fix should create group symlink on the secret and re-encrypt
    cli.run(["vars", "fix", "--flake", str(flake.path), "my_machine"])

    # Step 6: Assert all changes are committed (group symlinks + re-encrypted secrets are under vars/)
    git_status = run(
        ["git", "status", "--porcelain", "vars/", "sops/"],
    ).stdout.strip()
    assert git_status == "", (
        f"Expected no uncommitted changes after 'clan vars fix', got:\n{git_status}"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_groups_add_secret_commits_changes(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    sops_setup: SopsSetup,
) -> None:
    """Test that 'clan secrets groups add-secret' commits the group-to-secret symlink."""
    flake = flake_with_sops
    monkeypatch.chdir(flake.path)

    # Create a secret
    monkeypatch.setenv("SOPS_NIX_SECRET", "some_secret_value")
    cli.run(
        [
            "secrets",
            "set",
            "--flake",
            str(flake.path),
            "my_secret",
        ],
    )

    # Create a group with a user
    cli.run(["secrets", "groups", "add-user", "my_group", sops_setup.user])

    # Add the secret to the group
    cli.run(["secrets", "groups", "add-secret", "my_group", "my_secret"])

    # Assert: all sops/ changes are committed
    git_status = run(
        ["git", "status", "--porcelain", "sops/"],
    ).stdout.strip()
    assert git_status == "", (
        f"Expected no uncommitted sops/ changes after 'clan secrets groups add-secret', got:\n{git_status}"
    )
