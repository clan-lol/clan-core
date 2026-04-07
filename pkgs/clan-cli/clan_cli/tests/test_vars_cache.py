import argparse
import subprocess
from pathlib import Path

import pytest
from clan_cli.secrets.secrets import decrypt_secret
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.tests.helpers.flake_cache import invalidate_flake_cache
from clan_cli.vars.generate import generate_command
from clan_cli.vars.get import get_machine_var
from clan_cli.vars.public_modules import in_repo
from clan_cli.vars.secret_modules import password_store, sops
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import current_system
from clan_lib.nix_selectors import get_machine_prefix, vars_generators_metadata
from clan_lib.vars._types import GeneratorId, PerMachine
from clan_lib.vars.generate import (
    get_generators,
    run_generators,
)
from clan_lib.vars.generator import (
    Generator,
)
from clan_lib.vars.list import stringify_all_vars


@pytest.mark.broken_on_darwin
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
    assert value1 == value1_new, (
        "Value should not change without invalidation data being changed"
    )
    # set the invalidation data of the generator
    my_generator["validation"] = 1
    flake.refresh()
    # generate again and make sure the value changes
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    value2 = get_machine_var(machine, "my_generator/my_value").printable_value
    assert value1 != value2, "Value should change when invalidation data is changed"
    # generate again without changing invalidation data -> value should not change
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    value2_new = get_machine_var(machine, "my_generator/my_value").printable_value
    assert value2 == value2_new, (
        "Value should not change without invalidation data being changed"
    )
    # remove the validation data -> value should change again
    del my_generator["validation"]
    flake.refresh()
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    value3 = get_machine_var(machine, "my_generator/my_value").printable_value
    assert value2 != value3, "Value should change when invalidation data is changed"
    # generate again without changing invalidation data -> value should not change
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    value3_new = get_machine_var(machine, "my_generator/my_value").printable_value
    assert value3 == value3_new, (
        "Value should not change without invalidation data being changed"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_secret_var_password_store_minimal_select_calls(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    age_keys: list,
) -> None:
    """Test that password_store backend doesn't make unnecessary select calls."""
    config = flake.machines["my_machine"] = create_test_machine_config()
    clan_vars = config["clan"]["core"]["vars"]
    clan_vars["settings"]["secretStore"] = "password-store"
    # Use passage (age-based) instead of pass (GPG-based)
    config["clan"]["core"]["vars"]["password-store"]["passCommand"] = "passage"

    # Create a simple generator with a secret
    my_generator = clan_vars["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = 'echo hello > "$out"/my_secret'

    # Add machine2 and machine3 with the same configuration
    flake.machines["machine2"] = config.copy()
    flake.machines["machine3"] = config.copy()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Set up age key for passage using test fixtures
    age_key = age_keys[0]
    age_key_dir = flake.path / ".age"
    age_key_dir.mkdir()
    age_key_file = age_key_dir / "key.txt"
    age_key_file.write_text(age_key.privkey)

    # Set up password store directory for passage
    password_store_dir = flake.path / "pass"
    password_store_dir.mkdir(parents=True)
    # Create .age-recipients file for passage (passage uses this instead of .gpg-id)
    (password_store_dir / ".age-recipients").write_text(f"{age_key.pubkey}\n")

    # Passage uses PASSAGE_DIR (not PASSWORD_STORE_DIR like pass does)
    monkeypatch.setenv("PASSAGE_DIR", str(password_store_dir))
    # Set the age identities file for passage
    monkeypatch.setenv("PASSAGE_IDENTITIES_FILE", str(age_key_file))

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
    # Create an initial commit so the git repo is valid
    subprocess.run(
        ["git", "add", ".age-recipients"],
        cwd=password_store_dir,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initialize password store"],
        cwd=password_store_dir,
        check=True,
    )

    # Create a fresh flake object and invalidate cache to ensure clean state
    invalidate_flake_cache(flake.path)
    flake_obj = Flake(str(flake.path))

    # Generate the secret - this will initialize the password store backend
    # and should result in minimal select calls
    generate_command(
        argparse.Namespace(
            machines=["my_machine", "machine2", "machine3"],
            generator=None,
            flake=flake_obj,
            regenerate=False,
            no_sandbox=False,
        )
    )

    # The optimization should result in minimal cache misses.
    # We expect exactly 4 cache misses:
    # 1. Inventory selectors (from list_full_machines)
    # 2. relativeDirectory selector (from get_clan_dir in run_generators)
    # 3. Generator metadata selectors (from generate_command precache)
    # 4. finalScript and sops selectors (from run_generators precache)

    # Print stack traces if we have more cache misses than expected
    if flake_obj._cache_misses > 4:
        flake_obj.print_cache_miss_analysis(
            title="Cache miss analysis for password_store backend"
        )

    assert flake_obj._cache_misses == 4, (
        f"Expected exactly 4 cache misses for password_store backend, "
        f"got {flake_obj._cache_misses}."
    )

    # Verify the secret was actually generated
    store = password_store.SecretStore(flake=flake_obj)
    store.init_pass_command(machine="my_machine")
    generator = Generator(
        files=[],
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
    )
    assert store.exists(generator.key, "my_secret")
    assert store.get(generator.key, "my_secret").decode() == "hello\n"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_secret_var_sops_minimal_select_calls(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that sops backend doesn't make unnecessary select calls.

    This test uses multiple machines and multiple generators to ensure
    that the batching optimization works correctly across the board.
    """
    flake = flake_with_sops

    # Set up first machine with two generators
    machine1_config = flake.machines["machine1"] = create_test_machine_config()

    gen1_m1 = machine1_config["clan"]["core"]["vars"]["generators"]["gen1"]
    gen1_m1["files"]["secret1"]["secret"] = True
    gen1_m1["files"]["value1"]["secret"] = False
    gen1_m1["script"] = (
        'echo -n "secret1" > "$out"/secret1 && echo -n "value1" > "$out"/value1'
    )

    gen2_m1 = machine1_config["clan"]["core"]["vars"]["generators"]["gen2"]
    gen2_m1["files"]["secret2"]["secret"] = True
    gen2_m1["files"]["value2"]["secret"] = False
    gen2_m1["script"] = (
        'echo -n "secret2" > "$out"/secret2 && echo -n "value2" > "$out"/value2'
    )

    # Set up second machine with the same generator configuration
    flake.machines["machine2"] = machine1_config.copy()
    flake.machines["machine3"] = machine1_config.copy()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Create a fresh flake object and invalidate cache to ensure clean state
    invalidate_flake_cache(flake.path)
    flake_obj = Flake(str(flake.path))
    # Generate secrets for multiple machines - this should result in minimal select calls
    generate_command(
        argparse.Namespace(
            # don't select all machines, since this can trigger more eval calls
            # due to a difference in `all generators` vs `selected generators`
            machines=["machine1", "machine2"],
            generator=None,
            flake=flake_obj,
            regenerate=False,
            no_sandbox=False,
        )
    )
    # The optimization should result in minimal cache misses.
    # We expect exactly 4 cache misses:
    # 1. Inventory selectors (retrieving list of all machines)
    # 2. relativeDirectory selector (from get_clan_dir in run_generators)
    # 3. Generator metadata selectors (definitions of all generators + vars settings)
    # 4. finalScript and sops settings (from run_generators precache)

    # Print stack traces if we have more cache misses than expected
    if flake_obj._cache_misses > 4:
        flake_obj.print_cache_miss_analysis(
            title="Cache miss analysis for sops backend"
        )

    assert flake_obj._cache_misses == 4, (
        f"Expected exactly 4 cache misses for sops backend with 3 machines and 2 generators, "
        f"got {flake_obj._cache_misses}."
    )

    # Verify the secrets were actually generated for both machines
    sops_store = sops.SecretStore(flake=flake_obj)
    in_repo_store = in_repo.VarsStore(flake=flake_obj)

    for machine_name in ["machine1", "machine2"]:
        gen1 = Generator(
            _flake=flake_obj,
            key=GeneratorId(name="gen1", placement=PerMachine(machine_name)),
        )
        gen2 = Generator(
            _flake=flake_obj,
            key=GeneratorId(name="gen2", placement=PerMachine(machine_name)),
        )

        assert sops_store.exists(gen1.key, "secret1"), (
            f"secret1 missing for {machine_name}"
        )
        assert sops_store.get(gen1.key, "secret1").decode() == "secret1"
        assert in_repo_store.exists(gen1.key, "value1"), (
            f"value1 missing for {machine_name}"
        )
        assert in_repo_store.get(gen1.key, "value1").decode() == "value1"

        assert sops_store.exists(gen2.key, "secret2"), (
            f"secret2 missing for {machine_name}"
        )
        assert sops_store.get(gen2.key, "secret2").decode() == "secret2"
        assert in_repo_store.exists(gen2.key, "value2"), (
            f"value2 missing for {machine_name}"
        )
        assert in_repo_store.get(gen2.key, "value2").decode() == "value2"


@pytest.mark.broken_on_darwin
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

    # Test 1: Running vars generate for BOTH machines simultaneously should result in exactly 4 cache misses
    # Even though we have:
    # - 2 machines (my_machine and other_machine)
    # - 2 generators per machine (gen1 and gen2)
    # We get 4 cache misses when generating for both machines:
    # 1. Inventory selectors (from list_full_machines)
    # 2. relativeDirectory selector (from get_clan_dir in run_generators)
    # 3. Generator metadata selectors (from generate_command precache)
    # 4. finalScript selectors (from run_generators precache)

    generate_command(
        argparse.Namespace(
            machines=["my_machine", "other_machine"],
            generator=None,
            flake=flake_obj,
            regenerate=False,
            no_sandbox=False,
        )
    )

    # Print stack traces if we have more than 4 cache misses
    if flake_obj._cache_misses != 4:
        flake_obj.print_cache_miss_analysis(
            title="Cache miss analysis for vars generate"
        )

    assert flake_obj._cache_misses == 4, (
        f"Expected exactly 4 cache misses for vars generate, got {flake_obj._cache_misses}"
    )

    # Test 2: List all vars should result in exactly 1 cache miss
    # Force cache invalidation (this also resets cache miss tracking)
    invalidate_flake_cache(flake.path)
    flake_obj.invalidate_cache(reset_tracking=True)

    stringify_all_vars(machine1)
    assert flake_obj._cache_misses == 1, (
        f"Expected exactly 1 cache miss for vars list, got {flake_obj._cache_misses}"
    )

    # Test 3: Getting a specific var with a fresh cache should result in exactly 1 cache miss
    # Force cache invalidation (this also resets cache miss tracking)
    invalidate_flake_cache(flake.path)
    flake_obj.invalidate_cache(reset_tracking=True)

    # Only test gen1 for the get operation
    var_value = get_machine_var(machine1, "gen1/value1")
    assert var_value.printable_value == "test_value1"

    assert flake_obj._cache_misses == 1, (
        f"Expected exactly 1 cache miss for vars get with fresh cache, got {flake_obj._cache_misses}"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_dynamic_invalidation(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
) -> None:
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
    clan_flake.invalidate_cache(reset_tracking=True)
    monkeypatch.chdir(flake.path)

    # before generating, dependent generator validation should be empty; see bogus hardware-configuration.nix above
    # we have to avoid `*.files.value` in this initial select because the generators haven't been run yet
    # Generators 0: The initial generators before any 'vars generate'

    system = current_system()
    generators_0 = machine.flake.select(
        vars_generators_metadata(system, [machine.name])
    )[machine.name]
    assert generators_0["dependent_generator"]["validationHash"] is None

    # generate both my_generator and (the dependent) dependent_generator
    cli.run(["vars", "generate", "--flake", str(flake.path), machine.name])
    clan_flake.invalidate_cache(reset_tracking=True)

    # after generating once, dependent generator validation should be set
    # Generators_1: The generators after the first 'vars generate'

    prefix = get_machine_prefix()
    selector = f"{prefix}.{system}.{machine.name}.config.clan.core.vars.generators.*.{{validationHash,files}}"
    generators_1 = machine.flake.select(selector)
    assert generators_1["dependent_generator"]["validationHash"] is not None

    # Machine evaluation is highly expensive .
    # The generator will thus run again, and produce a different result in the second run.
    cli.run(["vars", "generate", "--flake", str(flake.path), machine.name])
    clan_flake.invalidate_cache(reset_tracking=True)
    # Generators_2: The generators after the second 'vars generate'
    generators_2 = machine.flake.select(selector)
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


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_generators_only_decrypts_requested_machines(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that get_generators only decrypts secrets for requested machines.

    This verifies the fix for the bug where `clan machines update <machine>`
    would try to decrypt secrets for all machines in the flake, not just the
    target machine. Users who don't have access to decrypt secrets for other
    machines should still be able to update their target machine.
    """
    flake = flake_with_sops

    # Create two machines with secret prompts
    m1_config = flake.machines["machine1"] = create_test_machine_config()
    m1_gen = m1_config["clan"]["core"]["vars"]["generators"]["my_generator"]
    m1_gen["prompts"]["secret_prompt"]["type"] = "hidden"
    m1_gen["prompts"]["secret_prompt"]["persist"] = True
    m1_gen["files"]["secret_prompt"]["secret"] = True

    m2_config = flake.machines["machine2"] = create_test_machine_config()
    m2_gen = m2_config["clan"]["core"]["vars"]["generators"]["my_generator"]
    m2_gen["prompts"]["secret_prompt"]["type"] = "hidden"
    m2_gen["prompts"]["secret_prompt"]["persist"] = True
    m2_gen["files"]["secret_prompt"]["secret"] = True

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Generate secrets for both machines
    run_generators(
        machines=[Machine(name="machine1", flake=Flake(str(flake.path)))],
        generators=["my_generator"],
        prompt_values={"my_generator": {"secret_prompt": "secret1"}},
    )
    run_generators(
        machines=[Machine(name="machine2", flake=Flake(str(flake.path)))],
        generators=["my_generator"],
        prompt_values={"my_generator": {"secret_prompt": "secret2"}},
    )

    # Track which secrets are decrypted
    decrypted_paths: list[Path] = []

    def tracking_decrypt(path: Path, age_plugins: list[str]) -> str:
        decrypted_paths.append(path)
        return decrypt_secret(path, age_plugins)

    # Patch where it's used, not where it's defined (the import happens at module load)
    monkeypatch.setattr(
        "clan_lib.vars.secret_modules.sops.decrypt_secret", tracking_decrypt
    )

    # Get generators for just machine1 with previous values
    machine1 = Machine(name="machine1", flake=Flake(str(flake.path)))
    generators = get_generators(
        machines=[machine1],
        full_closure=True,
    )

    # Verify we got the generator with previous value
    assert len(generators) == 1
    assert generators[0].name == "my_generator"
    assert generators[0].get_previous_value(generators[0].prompts[0]) == "secret1"

    # Verify we only decrypted machine1's secret, not machine2's
    decrypted_path_strs = [str(p) for p in decrypted_paths]
    assert any("machine1" in p for p in decrypted_path_strs), (
        f"Should have decrypted machine1's secret, got: {decrypted_path_strs}"
    )
    assert not any("machine2" in p for p in decrypted_path_strs), (
        f"Should NOT have decrypted machine2's secret, got: {decrypted_path_strs}"
    )
