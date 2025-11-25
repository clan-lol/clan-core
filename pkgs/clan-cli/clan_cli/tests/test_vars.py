import json
import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from clan_cli.tests.age_keys import SopsSetup
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.vars.check import check_vars
from clan_cli.vars.generator import (
    Generator,
    dependencies_as_dir,
)
from clan_cli.vars.get import get_machine_var
from clan_cli.vars.list import stringify_all_vars
from clan_cli.vars.public_modules import in_repo
from clan_cli.vars.secret_modules import password_store, sops
from clan_cli.vars.set import set_var
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config, nix_eval, run
from clan_lib.vars.generate import (
    get_generators,
    run_generators,
)


def invalidate_flake_cache(flake_path: Path) -> None:
    """Force flake cache invalidation by modifying the git repository.

    This adds a dummy file to git which changes the NAR hash of the flake,
    forcing a cache invalidation.
    """
    dummy_file = flake_path / f".cache_invalidation_{time.time()}"
    dummy_file.write_text("invalidate")
    run(["git", "add", str(dummy_file)])


def test_dependencies_as_files(temp_dir: Path) -> None:
    decrypted_dependencies = {
        "gen_1": {
            "var_1a": b"var_1a",
            "var_1b": b"var_1b",
        },
        "gen_2": {
            "var_2a": b"var_2a",
            "var_2b": b"var_2b",
        },
    }
    dependencies_as_dir(decrypted_dependencies, temp_dir)
    assert temp_dir.is_dir()
    assert (temp_dir / "gen_1" / "var_1a").read_bytes() == b"var_1a"
    assert (temp_dir / "gen_1" / "var_1b").read_bytes() == b"var_1b"
    assert (temp_dir / "gen_2" / "var_2a").read_bytes() == b"var_2a"
    assert (temp_dir / "gen_2" / "var_2b").read_bytes() == b"var_2b"
    # ensure the files are not world readable
    assert (temp_dir / "gen_1" / "var_1a").stat().st_mode & 0o777 == 0o600
    assert (temp_dir / "gen_1" / "var_1b").stat().st_mode & 0o777 == 0o600
    assert (temp_dir / "gen_2" / "var_2a").stat().st_mode & 0o777 == 0o600
    assert (temp_dir / "gen_2" / "var_2b").stat().st_mode & 0o777 == 0o600


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
    assert (
        "Update vars via generator my_generator for machine my_machine"
        in commit_message
    )
    assert (
        "Update vars via generator my_shared_generator for machine my_machine"
        in commit_message
    )
    public_value = get_machine_var(machine, "my_generator/my_value").printable_value
    assert public_value.startswith("public")
    shared_value = get_machine_var(
        machine,
        "my_shared_generator/my_shared_value",
    ).printable_value
    assert shared_value.startswith("shared")
    vars_text = stringify_all_vars(machine)
    flake_obj = Flake(str(flake.path))
    my_generator = Generator("my_generator", machines=["my_machine"], _flake=flake_obj)
    shared_generator = Generator(
        "my_shared_generator",
        share=True,
        machines=["my_machine"],
        _flake=flake_obj,
    )
    dependent_generator = Generator(
        "dependent_generator",
        machines=["my_machine"],
        _flake=flake_obj,
    )
    in_repo_store = in_repo.FactStore(flake=flake_obj)
    assert not in_repo_store.exists(my_generator, "my_secret")
    sops_store = sops.SecretStore(flake=flake_obj)
    assert sops_store.exists(my_generator, "my_secret")
    assert sops_store.get(my_generator, "my_secret").decode().startswith("secret")
    assert sops_store.exists(dependent_generator, "my_secret")
    secret_value = sops_store.get(dependent_generator, "my_secret").decode()
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
    secret_value_new = sops_store.get(dependent_generator, "my_secret").decode()
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
        dependent_generator,
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
    sops_store.delete(shared_generator, "my_shared_value")
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
    assert sops_store.exists(dependent_generator, "my_secret"), (
        "Dependent generator's secret should be generated"
    )
    secret_value_clean = sops_store.get(dependent_generator, "my_secret").decode()
    assert secret_value_clean == shared_value_clean, (
        "Dependent generator's secret should match the shared value"
    )


# TODO: it doesn't actually test if the group has access
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
        "first_generator",
        machines=["my_machine"],
        _flake=flake_obj,
    )
    second_generator = Generator(
        "second_generator",
        machines=["my_machine"],
        _flake=flake_obj,
    )
    in_repo_store = in_repo.FactStore(flake=flake_obj)
    assert not in_repo_store.exists(first_generator, "my_secret")
    sops_store = sops.SecretStore(flake=flake_obj)
    assert sops_store.exists(first_generator, "my_secret")
    assert sops_store.get(first_generator, "my_secret").decode() == "hello\n"
    assert sops_store.exists(second_generator, "my_secret")
    assert sops_store.get(second_generator, "my_secret").decode() == "hello\n"

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
        "first_generator",
        share=False,
        machines=["my_machine"],
        _flake=flake_obj,
    )
    second_generator_with_share = Generator(
        "second_generator",
        share=False,
        machines=["my_machine"],
        _flake=flake_obj,
    )
    assert sops_store.user_has_access("user2", first_generator_with_share, "my_secret")
    assert sops_store.user_has_access("user2", second_generator_with_share, "my_secret")

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
    assert sops_store.user_has_access("user2", first_generator_with_share, "my_secret")
    assert sops_store.user_has_access("user2", second_generator_with_share, "my_secret")


@pytest.mark.with_core
def test_generated_shared_secret_sops(
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
    flake.refresh()
    monkeypatch.chdir(flake.path)
    machine1 = Machine(name="machine1", flake=Flake(str(flake.path)))
    machine2 = Machine(name="machine2", flake=Flake(str(flake.path)))
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])

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
    assert check_vars(machine1.name, machine1.flake), (
        "machine1 has already generated vars, so check_vars should return True\n"
        f"Check result:\n{check_vars(machine1.name, machine1.flake)}"
    )
    # Verify no files were modified
    after_check_mtimes = get_file_mtimes(str(flake.path))
    assert initial_mtimes == after_check_mtimes, (
        "check_vars should not modify any files when vars are already valid"
    )

    assert not check_vars(machine2.name, machine2.flake), (
        "machine2 has not generated vars yet, so check_vars should return False"
    )
    # Verify no files were modified
    after_check_mtimes_2 = get_file_mtimes(str(flake.path))
    assert initial_mtimes == after_check_mtimes_2, (
        "check_vars should not modify any files when vars are not valid"
    )

    cli.run(["vars", "generate", "--flake", str(flake.path), "machine2"])
    m1_sops_store = sops.SecretStore(machine1.flake)
    m2_sops_store = sops.SecretStore(machine2.flake)
    # Create generators with machine context for testing
    generator_m1 = Generator(
        "my_shared_generator",
        share=True,
        _flake=machine1.flake,
    )
    generator_m2 = Generator(
        "my_shared_generator",
        share=True,
        _flake=machine2.flake,
    )

    assert m1_sops_store.exists(generator_m1, "my_shared_secret")
    assert m1_sops_store.exists(generator_m1, "no_deploy_secret")
    assert m2_sops_store.exists(generator_m2, "my_shared_secret")
    assert m2_sops_store.exists(generator_m2, "no_deploy_secret")
    assert m1_sops_store.machine_has_access(
        generator_m1, "my_shared_secret", "machine1"
    )
    assert m2_sops_store.machine_has_access(
        generator_m2, "my_shared_secret", "machine2"
    )
    assert not m1_sops_store.machine_has_access(
        generator_m1, "no_deploy_secret", "machine1"
    )
    assert not m2_sops_store.machine_has_access(
        generator_m2, "no_deploy_secret", "machine2"
    )


@pytest.mark.with_core
def test_generate_secret_var_password_store(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    test_root: Path,
) -> None:
    config = flake.machines["my_machine"] = create_test_machine_config()
    clan_vars = config["clan"]["core"]["vars"]
    clan_vars["settings"]["secretStore"] = "password-store"
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
        "my_generator",
        share=False,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    my_generator_shared = Generator(
        "my_generator",
        share=True,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    my_shared_generator = Generator(
        "my_shared_generator",
        share=True,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    my_shared_generator_not_shared = Generator(
        "my_shared_generator",
        share=False,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    assert store.exists(my_generator, "my_secret")
    assert not store.exists(my_generator_shared, "my_secret")
    assert store.exists(my_shared_generator, "my_shared_secret")
    assert not store.exists(my_shared_generator_not_shared, "my_shared_secret")

    generator = Generator(
        name="my_generator",
        share=False,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    assert store.get(generator, "my_secret").decode() == "hello\n"
    vars_text = stringify_all_vars(machine)
    assert "my_generator/my_secret" in vars_text

    my_generator = Generator(
        "my_generator",
        share=False,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    var_name = "my_secret"
    store.delete(my_generator, var_name)
    assert not store.exists(my_generator, var_name)

    store.delete_store("my_machine")
    store.delete_store("my_machine")  # check idempotency
    my_generator2 = Generator(
        "my_generator2",
        share=False,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    var_name = "my_secret2"
    assert not store.exists(my_generator2, var_name)

    # The shared secret should still be there,
    # not sure if we can delete those automatically:
    my_shared_generator = Generator(
        "my_shared_generator",
        share=True,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )
    var_name = "my_shared_secret"
    assert store.exists(my_shared_generator, var_name)


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
    in_repo_store1 = in_repo.FactStore(flake=flake_obj)
    in_repo_store2 = in_repo.FactStore(flake=flake_obj)

    # Create generators for each machine
    gen1 = Generator("my_generator", machines=["machine1"], _flake=flake_obj)
    gen2 = Generator("my_generator", machines=["machine2"], _flake=flake_obj)

    assert in_repo_store1.exists(gen1, "my_value")
    assert in_repo_store2.exists(gen2, "my_value")
    assert in_repo_store1.get(gen1, "my_value").decode() == "machine1\n"
    assert in_repo_store2.get(gen2, "my_value").decode() == "machine2\n"
    # check if secret vars have been created correctly
    sops_store1 = sops.SecretStore(flake=flake_obj)
    sops_store2 = sops.SecretStore(flake=flake_obj)
    assert sops_store1.exists(gen1, "my_secret")
    assert sops_store2.exists(gen2, "my_secret")
    assert sops_store1.get(gen1, "my_secret").decode() == "machine1\n"
    assert sops_store2.get(gen2, "my_secret").decode() == "machine2\n"


@pytest.mark.with_core
def test_prompt(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that generators can use prompts to collect user input and store the values appropriately."""
    flake = flake_with_sops

    # Configure the machine and generator
    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]

    # Define output files - these will contain the prompt responses
    my_generator["files"]["line_value"]["secret"] = False  # Public file
    my_generator["files"]["multiline_value"]["secret"] = False  # Public file

    # Configure prompts that will collect user input
    # prompt1: Single line input, not persisted (temporary)
    my_generator["prompts"]["prompt1"]["description"] = "dream2nix"
    my_generator["prompts"]["prompt1"]["persist"] = False
    my_generator["prompts"]["prompt1"]["type"] = "line"

    # prompt2: Single line input, not persisted (temporary)
    my_generator["prompts"]["prompt2"]["description"] = "dream2nix"
    my_generator["prompts"]["prompt2"]["persist"] = False
    my_generator["prompts"]["prompt2"]["type"] = "line"

    # prompt_persist: This prompt will be stored as a secret for reuse
    my_generator["prompts"]["prompt_persist"]["persist"] = True

    # Script that reads prompt responses and writes them to output files
    my_generator["script"] = (
        'cat "$prompts"/prompt1 > "$out"/line_value; cat "$prompts"/prompt2 > "$out"/multiline_value'
    )

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Mock the prompt responses to simulate user input
    monkeypatch.setattr(
        "clan_cli.vars.prompt.MOCK_PROMPT_RESPONSE",
        iter(["line input", "my\nmultiline\ninput\n", "prompt_persist"]),
    )

    # Run the generator which will collect prompts and generate vars
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])

    # Set up objects for testing the results
    flake_obj = Flake(str(flake.path))
    my_generator = Generator("my_generator", machines=["my_machine"], _flake=flake_obj)
    my_generator_with_details = Generator(
        name="my_generator",
        share=False,
        files=[],
        machines=["my_machine"],
        _flake=flake_obj,
    )

    # Verify that non-persistent prompts created public vars correctly
    in_repo_store = in_repo.FactStore(flake=flake_obj)
    assert in_repo_store.exists(my_generator, "line_value")
    assert in_repo_store.get(my_generator, "line_value").decode() == "line input"

    assert in_repo_store.exists(my_generator, "multiline_value")
    assert (
        in_repo_store.get(my_generator, "multiline_value").decode()
        == "my\nmultiline\ninput\n"
    )

    # Verify that persistent prompt was stored as a secret
    sops_store = sops.SecretStore(flake=flake_obj)
    assert sops_store.exists(my_generator_with_details, "prompt_persist")
    assert sops_store.get(my_generator, "prompt_persist").decode() == "prompt_persist"


@pytest.mark.with_core
def test_non_existing_dependency_raises_error(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure that a generator with a non-existing dependency raises a clear error."""
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = 'echo "$RANDOM" > "$out"/my_value'
    my_generator["dependencies"] = ["non_existing_generator"]
    flake.refresh()
    monkeypatch.chdir(flake.path)
    with pytest.raises(
        ClanError,
        match="Generator 'my_generator' on machine 'my_machine' depends on generator 'non_existing_generator', but 'non_existing_generator' does not exist",
    ):
        cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])


@pytest.mark.with_core
def test_shared_vars_must_never_depend_on_machine_specific_vars(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure that shared vars never depend on machine specific vars."""
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["share"] = True
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = 'echo "$RANDOM" > "$out"/my_value'
    my_generator["dependencies"] = ["machine_specific_generator"]
    machine_specific_generator = config["clan"]["core"]["vars"]["generators"][
        "machine_specific_generator"
    ]
    machine_specific_generator["share"] = False
    machine_specific_generator["files"]["my_value"]["secret"] = False
    machine_specific_generator["script"] = 'echo "$RANDOM" > "$out"/my_value'
    flake.refresh()
    monkeypatch.chdir(flake.path)
    # make sure an Exception is raised when trying to generate vars
    with pytest.raises(
        ClanError,
        match="Shared generators must not depend on machine specific generators",
    ):
        cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])


@pytest.mark.with_core
def test_shared_vars_regeneration(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure that is a shared generator gets generated on one machine, dependents of that
    shared generator on other machines get re-generated as well.
    """
    flake = flake_with_sops

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_generator = machine1_config["clan"]["core"]["vars"]["generators"][
        "shared_generator"
    ]
    shared_generator["share"] = True
    shared_generator["files"]["my_value"]["secret"] = False
    shared_generator["script"] = 'echo "$RANDOM" > "$out"/my_value'
    child_generator = machine1_config["clan"]["core"]["vars"]["generators"][
        "child_generator"
    ]
    child_generator["share"] = False
    child_generator["files"]["my_value"]["secret"] = False
    child_generator["dependencies"] = ["shared_generator"]
    child_generator["script"] = 'cat "$in"/shared_generator/my_value > "$out"/my_value'
    # machine 2 is equivalent to machine 1
    flake.machines["machine2"] = machine1_config
    # machine 0 is a machine with no relevant generators
    # This tests regression: https://git.clan.lol/clan/clan-core/issues/5747
    # ... where shared vars defined only on some machines lead to an eval errors
    flake.machines["machine0"] = create_test_machine_config()
    flake.refresh()
    monkeypatch.chdir(flake.path)
    machine1 = Machine(name="machine1", flake=Flake(str(flake.path)))
    machine2 = Machine(name="machine2", flake=Flake(str(flake.path)))
    in_repo_store_1 = in_repo.FactStore(machine1.flake)
    in_repo_store_2 = in_repo.FactStore(machine2.flake)
    # Create generators with machine context for testing
    child_gen_m1 = Generator(
        "child_generator", share=False, machines=["machine1"], _flake=machine1.flake
    )
    child_gen_m2 = Generator(
        "child_generator", share=False, machines=["machine2"], _flake=machine2.flake
    )
    cli.run(["vars", "generate", "--flake", str(flake.path)])
    # generate for machine 1
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])
    # generate for machine 2
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine2"])
    # child value should be the same on both machines
    assert in_repo_store_1.get(child_gen_m1, "my_value") == in_repo_store_2.get(
        child_gen_m2, "my_value"
    ), "Child values should be the same after initial generation"

    # regenerate on all machines
    cli.run(
        ["vars", "generate", "--flake", str(flake.path), "--regenerate"],
    )
    # ensure child value after --regenerate is the same on both machines
    assert in_repo_store_1.get(child_gen_m1, "my_value") == in_repo_store_2.get(
        child_gen_m2, "my_value"
    ), "Child values should be the same after regenerating all machines"

    # regenerate for machine 1
    cli.run(
        ["vars", "generate", "--flake", str(flake.path), "machine1", "--regenerate"]
    )
    # ensure child value after --regenerate is the same on both machines
    assert in_repo_store_1.get(child_gen_m1, "my_value") == in_repo_store_2.get(
        child_gen_m2, "my_value"
    ), "Child values should be the same after regenerating machine1"


@pytest.mark.with_core
def test_multi_machine_shared_vars(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure that shared vars are regenerated only when they should, and also can be
    accessed by all machines that should have access.

    Specifically:
        - make sure shared wars are not regenerated when a second machines is added
        - make sure vars can still be accessed by all machines, after they are regenerated
    """
    flake = flake_with_sops

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_generator = machine1_config["clan"]["core"]["vars"]["generators"][
        "shared_generator"
    ]
    shared_generator["share"] = True
    shared_generator["files"]["my_secret"]["secret"] = True
    shared_generator["files"]["my_value"]["secret"] = False
    shared_generator["script"] = (
        'echo "$RANDOM" > "$out"/my_value && echo "$RANDOM" > "$out"/my_secret'
    )
    # machine 2 is equivalent to machine 1
    flake.machines["machine2"] = machine1_config
    flake.refresh()
    monkeypatch.chdir(flake.path)
    machine1 = Machine(name="machine1", flake=Flake(str(flake.path)))
    machine2 = Machine(name="machine2", flake=Flake(str(flake.path)))
    sops_store_1 = sops.SecretStore(machine1.flake)
    sops_store_2 = sops.SecretStore(machine2.flake)
    in_repo_store_1 = in_repo.FactStore(machine1.flake)
    in_repo_store_2 = in_repo.FactStore(machine2.flake)
    # Create generators with machine context for testing
    generator_m1 = Generator(
        "shared_generator",
        share=True,
        machines=["machine1"],
        _flake=machine1.flake,
    )
    generator_m2 = Generator(
        "shared_generator",
        share=True,
        machines=["machine2"],
        _flake=machine2.flake,
    )
    # generate for machine 1
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])
    # read out values for machine 1
    m1_secret = sops_store_1.get(generator_m1, "my_secret")
    m1_value = in_repo_store_1.get(generator_m1, "my_value")
    # generate for machine 2
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine2"])
    # ensure values are the same for both machines
    assert sops_store_2.get(generator_m2, "my_secret") == m1_secret
    assert in_repo_store_2.get(generator_m2, "my_value") == m1_value

    # ensure shared secret stays available for all machines after regeneration
    # regenerate for machine 1
    cli.run(
        ["vars", "generate", "--flake", str(flake.path), "machine1", "--regenerate"],
    )
    # ensure values changed
    new_secret_1 = sops_store_1.get(generator_m1, "my_secret")
    new_value_1 = in_repo_store_1.get(generator_m1, "my_value")
    new_secret_2 = sops_store_2.get(generator_m2, "my_secret")
    assert new_secret_1 != m1_secret
    assert new_value_1 != m1_value
    # ensure that both machines still have access to the same secret
    assert new_secret_1 == new_secret_2
    assert sops_store_1.machine_has_access(generator_m1, "my_secret", "machine1")
    assert sops_store_2.machine_has_access(generator_m2, "my_secret", "machine2")


@pytest.mark.with_core
def test_api_set_prompts(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["prompts"]["prompt1"]["type"] = "line"
    my_generator["prompts"]["prompt1"]["persist"] = True
    my_generator["files"]["prompt1"]["secret"] = False
    flake.refresh()

    monkeypatch.chdir(flake.path)

    run_generators(
        machines=[Machine(name="my_machine", flake=Flake(str(flake.path)))],
        generators=["my_generator"],
        prompt_values={
            "my_generator": {
                "prompt1": "input1",
            },
        },
    )
    machine = Machine(name="my_machine", flake=Flake(str(flake.path)))
    store = in_repo.FactStore(machine.flake)
    my_generator = Generator(
        "my_generator", machines=["my_machine"], _flake=machine.flake
    )
    assert store.exists(my_generator, "prompt1")
    assert store.get(my_generator, "prompt1").decode() == "input1"
    run_generators(
        machines=[Machine(name="my_machine", flake=Flake(str(flake.path)))],
        generators=["my_generator"],
        prompt_values={
            "my_generator": {
                "prompt1": "input2",
            },
        },
    )
    assert store.get(my_generator, "prompt1").decode() == "input2"

    machine = Machine(name="my_machine", flake=Flake(str(flake.path)))
    generators = get_generators(
        machines=[machine],
        full_closure=True,
        include_previous_values=True,
    )
    # get_generators should bind the store
    assert generators[0].files[0]._store is not None

    assert len(generators) == 1
    assert generators[0].name == "my_generator"
    assert generators[0].prompts[0].name == "prompt1"
    assert generators[0].prompts[0].previous_value == "input2"


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

    assert "Updated var my_generator/my_value" in caplog.text
    assert "old: <not set>" in caplog.text
    assert "new: hello" in caplog.text
    caplog.clear()

    set_var("my_machine", "my_generator/my_value", b"world", flake)
    with caplog.at_level(logging.INFO):
        run_generators(
            machines=[Machine(name="my_machine", flake=flake)],
            generators=["my_generator"],
        )
    assert "Updated var my_generator/my_value" in caplog.text
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
    assert "Updated secret var my_secret_generator/my_secret" in caplog.text
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


@pytest.mark.with_core
def test_migration(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    caplog: pytest.LogCaptureFixture,
) -> None:
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    my_service = config["clan"]["core"]["facts"]["services"]["my_service"]
    my_service["public"]["my_value"] = {}
    my_service["secret"]["my_secret"] = {}
    my_service["generator"]["script"] = (
        'echo -n hello > "$facts"/my_value && echo -n hello > "$secrets"/my_secret'
    )
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["migrateFact"] = "my_service"
    my_generator["script"] = 'echo -n other > "$out"/my_value'

    other_service = config["clan"]["core"]["facts"]["services"]["other_service"]
    other_service["secret"]["other_value"] = {}
    other_service["generator"]["script"] = 'echo -n hello > "$secrets"/other_value'
    other_generator = config["clan"]["core"]["vars"]["generators"]["other_generator"]
    # the var to migrate to is mistakenly marked as not secret (migration should fail)
    other_generator["files"]["other_value"]["secret"] = False
    other_generator["migrateFact"] = "my_service"
    other_generator["script"] = 'echo -n value-from-vars > "$out"/other_value'

    flake.refresh()
    monkeypatch.chdir(flake.path)
    cli.run(["facts", "generate", "--flake", str(flake.path), "my_machine"])
    with caplog.at_level(logging.INFO):
        cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])

    assert "Migrated var my_generator/my_value" in caplog.text
    assert "Migrated secret var my_generator/my_secret" in caplog.text
    flake_obj = Flake(str(flake.path))
    my_generator = Generator("my_generator", machines=["my_machine"], _flake=flake_obj)
    other_generator = Generator(
        "other_generator",
        machines=["my_machine"],
        _flake=flake_obj,
    )
    in_repo_store = in_repo.FactStore(flake=flake_obj)
    sops_store = sops.SecretStore(flake=flake_obj)
    assert in_repo_store.exists(my_generator, "my_value")
    assert in_repo_store.get(my_generator, "my_value").decode() == "hello"
    assert sops_store.exists(my_generator, "my_secret")
    assert sops_store.get(my_generator, "my_secret").decode() == "hello"

    assert in_repo_store.exists(other_generator, "other_value")
    assert (
        in_repo_store.get(other_generator, "other_value").decode() == "value-from-vars"
    )


@pytest.mark.with_core
def test_fails_when_files_are_left_from_other_backend(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    my_secret_generator = config["clan"]["core"]["vars"]["generators"][
        "my_secret_generator"
    ]
    my_secret_generator["files"]["my_secret"]["secret"] = True
    my_secret_generator["script"] = 'echo hello > "$out"/my_secret'
    my_value_generator = config["clan"]["core"]["vars"]["generators"][
        "my_value_generator"
    ]
    my_value_generator["files"]["my_value"]["secret"] = False
    my_value_generator["script"] = 'echo hello > "$out"/my_value'
    flake.refresh()
    monkeypatch.chdir(flake.path)
    for generator in ["my_secret_generator", "my_value_generator"]:
        run_generators(
            machines=[Machine(name="my_machine", flake=Flake(str(flake.path)))],
            generators=generator,
        )
    # Will raise. It was secret before, but now it's not.
    my_secret_generator["files"]["my_secret"]["secret"] = (
        False  # secret -> public (NOT OK)
    )
    # WIll not raise. It was not secret before, and it's secret now.
    my_value_generator["files"]["my_value"]["secret"] = True  # public -> secret (OK)
    flake.refresh()
    monkeypatch.chdir(flake.path)
    for generator in ["my_secret_generator", "my_value_generator"]:
        # This should raise an error
        if generator == "my_secret_generator":
            with pytest.raises(ClanError):
                run_generators(
                    machines=[Machine(name="my_machine", flake=Flake(str(flake.path)))],
                    generators=generator,
                )
        else:
            run_generators(
                machines=[Machine(name="my_machine", flake=Flake(str(flake.path)))],
                generators=generator,
            )


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


@pytest.mark.with_core
def test_invalidation(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = 'echo -n "$RANDOM" > "$out"/my_value'
    flake.refresh()
    monkeypatch.chdir(flake.path)
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    machine = Machine(name="my_machine", flake=Flake(str(flake.path)))
    value1 = get_machine_var(machine, "my_generator/my_value").printable_value
    # generate again and make sure nothing changes without the invalidation data being set
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    value1_new = get_machine_var(machine, "my_generator/my_value").printable_value
    assert value1 == value1_new
    # set the invalidation data of the generator
    my_generator["validation"] = 1
    flake.refresh()
    # generate again and make sure the value changes
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    value2 = get_machine_var(machine, "my_generator/my_value").printable_value
    assert value1 != value2
    # generate again without changing invalidation data -> value should not change
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    value2_new = get_machine_var(machine, "my_generator/my_value").printable_value
    assert value2 == value2_new


@pytest.mark.with_core
def test_share_mode_switch_regenerates_secret(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that switching a generator from share=false to share=true
    causes the secret to be regenerated with a new value.
    """
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()

    # Create a generator with share=false initially
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["share"] = False
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = (
        'echo -n "public$RANDOM" > "$out"/my_value && echo -n "secret$RANDOM" > "$out"/my_secret'
    )

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Generate with share=false
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])

    # Read the initial values
    flake_obj = Flake(str(flake.path))
    in_repo_store = in_repo.FactStore(flake=flake_obj)
    sops_store = sops.SecretStore(flake=flake_obj)

    generator_not_shared = Generator(
        "my_generator", share=False, machines=["my_machine"], _flake=flake_obj
    )

    initial_public = in_repo_store.get(generator_not_shared, "my_value").decode()
    initial_secret = sops_store.get(generator_not_shared, "my_secret").decode()

    # Verify initial values exist and have expected format
    assert initial_public.startswith("public")
    assert initial_secret.startswith("secret")

    # Now switch to share=true
    my_generator["share"] = True
    flake.refresh()

    # Generate again with share=true
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])

    # Read the new values with shared generator
    generator_shared = Generator(
        "my_generator", share=True, machines=["my_machine"], _flake=flake_obj
    )

    new_public = in_repo_store.get(generator_shared, "my_value").decode()
    new_secret = sops_store.get(generator_shared, "my_secret").decode()

    # Verify that both values have changed (regenerated)
    assert new_public != initial_public, (
        "Public value should be regenerated when switching to share=true"
    )
    assert new_secret != initial_secret, (
        "Secret value should be regenerated when switching to share=true"
    )

    # Verify new values still have expected format
    assert new_public.startswith("public")
    assert new_secret.startswith("secret")

    # Verify the old machine-specific secret no longer exists
    assert not sops_store.exists(generator_not_shared, "my_secret"), (
        "Machine-specific secret should be removed"
    )

    # Verify the new shared secret exists
    assert sops_store.exists(generator_shared, "my_secret"), (
        "Shared secret should exist"
    )


@pytest.mark.with_core
def test_cache_misses_for_vars_operations(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    """Test that vars operations result in minimal cache misses."""
    # Set up first machine with two generators
    config = flake.machines["my_machine"] = create_test_machine_config()

    # Set up two generators with public values
    gen1 = config["clan"]["core"]["vars"]["generators"]["gen1"]
    gen1["files"]["value1"]["secret"] = False
    gen1["script"] = 'echo -n "test_value1" > "$out"/value1'

    gen2 = config["clan"]["core"]["vars"]["generators"]["gen2"]
    gen2["files"]["value2"]["secret"] = False
    gen2["script"] = 'echo -n "test_value2" > "$out"/value2'

    # Add a second machine with the same generator configuration
    flake.machines["other_machine"] = config.copy()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Create fresh machine objects to ensure clean cache state
    flake_obj = Flake(str(flake.path))
    machine1 = Machine(name="my_machine", flake=flake_obj)
    machine2 = Machine(name="other_machine", flake=flake_obj)

    # Test 1: Running vars generate for BOTH machines simultaneously should still result in exactly 2 cache misses
    # Even though we have:
    # - 2 machines (my_machine and other_machine)
    # - 2 generators per machine (gen1 and gen2)
    # We still only get 2 cache misses when generating for both machines:
    # 1. One for getting the list of generators for both machines
    # 2. One batched evaluation for getting all generator scripts for both machines
    # The key insight: the system should batch ALL evaluations across ALL machines into a single nix eval

    run_generators(
        machines=[machine1, machine2],
        generators=None,  # Generate all
    )

    # Print stack traces if we have more than 2 cache misses
    if flake_obj._cache_misses != 2:
        flake_obj.print_cache_miss_analysis(
            title="Cache miss analysis for vars generate"
        )

    assert flake_obj._cache_misses == 2, (
        f"Expected exactly 2 cache misses for vars generate, got {flake_obj._cache_misses}"
    )

    # Test 2: List all vars should result in exactly 1 cache miss
    # Force cache invalidation (this also resets cache miss tracking)
    invalidate_flake_cache(flake.path)
    flake_obj.invalidate_cache()

    stringify_all_vars(machine1)
    assert flake_obj._cache_misses == 1, (
        f"Expected exactly 1 cache miss for vars list, got {flake_obj._cache_misses}"
    )

    # Test 3: Getting a specific var with a fresh cache should result in exactly 1 cache miss
    # Force cache invalidation (this also resets cache miss tracking)
    invalidate_flake_cache(flake.path)
    flake_obj.invalidate_cache()

    # Only test gen1 for the get operation
    var_value = get_machine_var(machine1, "gen1/value1")
    assert var_value.printable_value == "test_value1"

    assert flake_obj._cache_misses == 1, (
        f"Expected exactly 1 cache miss for vars get with fresh cache, got {flake_obj._cache_misses}"
    )


@pytest.mark.with_core
def test_shared_generator_conflicting_definition_raises_error(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that vars generation raises an error when two machines have different
    definitions for the same shared generator.
    """
    flake = flake_with_sops

    # Create machine1 with a shared generator
    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_gen1 = machine1_config["clan"]["core"]["vars"]["generators"][
        "shared_generator"
    ]
    shared_gen1["share"] = True
    shared_gen1["files"]["file1"]["secret"] = False
    shared_gen1["script"] = 'echo "test" > "$out"/file1'

    # Create machine2 with the same shared generator but different files
    machine2_config = flake.machines["machine2"] = create_test_machine_config()
    shared_gen2 = machine2_config["clan"]["core"]["vars"]["generators"][
        "shared_generator"
    ]
    shared_gen2["share"] = True
    shared_gen2["files"]["file2"]["secret"] = False  # Different file name
    shared_gen2["script"] = 'echo "test" > "$out"/file2'

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Attempting to generate vars for both machines should raise an error
    # because they have conflicting definitions for the same shared generator
    with pytest.raises(
        ClanError,
        match=r".*differ.*",
    ):
        cli.run(["vars", "generate", "--flake", str(flake.path)])


@pytest.mark.with_core
def test_dynamic_invalidation(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
    gen_prefix = "config.clan.core.vars.generators"

    clan_flake = Flake(str(flake.path))
    machine = Machine(name="my_machine", flake=clan_flake)

    config = flake.machines[machine.name] = create_test_machine_config()

    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = 'echo -n "$RANDOM" > "$out"/my_value'

    dependent_generator = config["clan"]["core"]["vars"]["generators"][
        "dependent_generator"
    ]
    dependent_generator["files"]["my_value"]["secret"] = False
    dependent_generator["dependencies"] = ["my_generator"]
    dependent_generator["script"] = 'echo -n "$RANDOM" > "$out"/my_value'

    flake.refresh()

    # this is an abuse
    custom_nix = flake.path / "machines" / machine.name / "hardware-configuration.nix"
    # Set the validation such that we have a ValidationHash
    # The validationHash changes every time, if the my_generator.files.my_value.value changes
    # So every time we re-generate, the dependent_generator should also re-generate.
    # This however is the case anyways. So i dont understand why we have validationHash here.
    custom_nix.write_text(
        """
        { config, ... }: let
            p = config.clan.core.vars.generators.my_generator.files.my_value.flakePath;
        in {
            clan.core.vars.generators.dependent_generator.validation = if builtins.pathExists p then builtins.readFile p else null;
        }
    """,
    )

    flake.refresh()
    clan_flake.invalidate_cache()
    monkeypatch.chdir(flake.path)

    # before generating, dependent generator validation should be empty; see bogus hardware-configuration.nix above
    # we have to avoid `*.files.value` in this initial select because the generators haven't been run yet
    # Generators 0: The initial generators before any 'vars generate'
    generators_0 = machine.select(f"{gen_prefix}.*.{{validationHash}}")
    assert generators_0["dependent_generator"]["validationHash"] is None

    # generate both my_generator and (the dependent) dependent_generator
    cli.run(["vars", "generate", "--flake", str(flake.path), machine.name])
    clan_flake.invalidate_cache()

    # after generating once, dependent generator validation should be set
    # Generators_1: The generators after the first 'vars generate'
    generators_1 = machine.select(gen_prefix)
    assert generators_1["dependent_generator"]["validationHash"] is not None

    # @tangential: after generating once, neither generator should want to run again because `clan vars generate` should have re-evaluated the dependent generator's validationHash after executing the parent generator but before executing the dependent generator
    # this ensures that validation can depend on parent generators while still only requiring a single pass
    #
    # @hsjobeki: The above sentence is incorrect we don't re-evaluate in between generator runs.
    # Otherwise we would need to evaluate all machines N-times. Resulting in M*N evaluations each beeing very expensive.
    # Machine evaluation is highly expensive .
    # The generator will thus run again, and produce a different result in the second run.
    cli.run(["vars", "generate", "--flake", str(flake.path), machine.name])
    clan_flake.invalidate_cache()
    # Generators_2: The generators after the second 'vars generate'
    generators_2 = machine.select(gen_prefix)
    assert (
        generators_1["dependent_generator"]["validationHash"]
        == generators_2["dependent_generator"]["validationHash"]
    )
    assert (
        generators_1["my_generator"]["files"]["my_value"]["value"]
        == generators_2["my_generator"]["files"]["my_value"]["value"]
    )
    # The generator value will change on the second run. Because the validationHash changes after the generation.
    # Previously: it changed during generation because we would re-evaluate the flake N-times after each generator was settled.
    # Due to performance reasons, we cannot do this anymore
    assert (
        generators_1["dependent_generator"]["files"]["my_value"]["value"]
        != generators_2["dependent_generator"]["files"]["my_value"]["value"]
    )
