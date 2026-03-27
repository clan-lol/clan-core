import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.vars.public_modules import in_repo
from clan_cli.vars.secret_modules import sops
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import run
from clan_lib.vars._types import GeneratorId, PerMachine, Shared
from clan_lib.vars.generator import (
    Generator,
)


@pytest.mark.broken_on_darwin
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
    in_repo_store_1 = in_repo.VarsStore(machine1.flake)
    in_repo_store_2 = in_repo.VarsStore(machine2.flake)
    # Create generators with machine context for testing
    child_gen_m1 = Generator(
        _flake=machine1.flake,
        key=GeneratorId(name="child_generator", placement=PerMachine("machine1")),
    )
    child_gen_m2 = Generator(
        _flake=machine2.flake,
        key=GeneratorId(name="child_generator", placement=PerMachine("machine2")),
    )
    cli.run(["vars", "generate", "--flake", str(flake.path)])
    # generate for machine 1
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])
    # generate for machine 2
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine2"])
    # child value should be the same on both machines
    assert in_repo_store_1.get(child_gen_m1.key, "my_value") == in_repo_store_2.get(
        child_gen_m2.key, "my_value"
    ), "Child values should be the same after initial generation"

    # regenerate on all machines
    cli.run(
        ["vars", "generate", "--flake", str(flake.path), "--regenerate"],
    )
    # ensure child value after --regenerate is the same on both machines
    assert in_repo_store_1.get(child_gen_m1.key, "my_value") == in_repo_store_2.get(
        child_gen_m2.key, "my_value"
    ), "Child values should be the same after regenerating all machines"

    # regenerate for machine 1
    cli.run(
        ["vars", "generate", "--flake", str(flake.path), "machine1", "--regenerate"]
    )
    # ensure child value after --regenerate is the same on both machines
    assert in_repo_store_1.get(child_gen_m1.key, "my_value") == in_repo_store_2.get(
        child_gen_m2.key, "my_value"
    ), "Child values should be the same after regenerating machine1"


@pytest.mark.broken_on_darwin
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
    in_repo_store_1 = in_repo.VarsStore(machine1.flake)
    in_repo_store_2 = in_repo.VarsStore(machine2.flake)
    # Create generators with machine context for testing
    generator_m1 = Generator(
        _flake=machine1.flake,
        key=GeneratorId(name="shared_generator", placement=Shared()),
    )
    generator_m2 = Generator(
        _flake=machine2.flake,
        key=GeneratorId(name="shared_generator", placement=Shared()),
    )
    # generate for machine 1
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])
    # read out values for machine 1
    m1_secret = sops_store_1.get(generator_m1.key, "my_secret")
    m1_value = in_repo_store_1.get(generator_m1.key, "my_value")
    # generate for machine 2
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine2"])
    # ensure values are the same for both machines
    assert sops_store_2.get(generator_m2.key, "my_secret") == m1_secret
    assert in_repo_store_2.get(generator_m2.key, "my_value") == m1_value

    # ensure shared secret stays available for all machines after regeneration
    # regenerate for machine 1
    cli.run(
        ["vars", "generate", "--flake", str(flake.path), "machine1", "--regenerate"],
    )
    # ensure values changed
    new_secret_1 = sops_store_1.get(generator_m1.key, "my_secret")
    new_value_1 = in_repo_store_1.get(generator_m1.key, "my_value")
    new_secret_2 = sops_store_2.get(generator_m2.key, "my_secret")
    assert new_secret_1 != m1_secret
    assert new_value_1 != m1_value
    # ensure that both machines still have access to the same secret
    assert new_secret_1 == new_secret_2
    assert sops_store_1.machine_has_access(generator_m1.key, "my_secret", "machine1")
    assert sops_store_2.machine_has_access(generator_m2.key, "my_secret", "machine2")


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_add_machine_to_existing_shared_secret(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that a machine added after initial generation gets access without regeneration.

    This tests the scenario where:
    1. Machine1 is configured and generates a shared secret
    2. Machine2 is added to the config AFTER the secret exists (with the shared generator)
    3. Machine2 should get access without the secret being regenerated
    4. Machine3 is added WITHOUT the shared generator and should NOT have access
    """
    flake = flake_with_sops

    # Step 1: Configure only machine1 with a shared generator
    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_generator = machine1_config["clan"]["core"]["vars"]["generators"][
        "shared_generator"
    ]
    shared_generator["share"] = True
    shared_generator["files"]["my_secret"]["secret"] = True
    shared_generator["script"] = 'echo "$RANDOM" > "$out"/my_secret'
    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Step 2: Generate for machine1 - creates the shared secret
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine1"])

    # Read the secret value for machine1
    machine1 = Machine(name="machine1", flake=Flake(str(flake.path)))
    sops_store = sops.SecretStore(machine1.flake)
    generator_key = GeneratorId(name="shared_generator", placement=Shared())
    original_secret = sops_store.get(generator_key, "my_secret")

    # Verify machine1 has access
    assert sops_store.machine_has_access(generator_key, "my_secret", "machine1")

    # Step 3: Add machine2 to config AFTER the secret exists
    machine2_config = flake.machines["machine2"] = create_test_machine_config()
    machine2_config["clan"]["core"]["vars"]["generators"]["shared_generator"] = (
        shared_generator.copy()
    )
    flake.refresh()

    # Step 4: Generate for machine2 - should add machine2 via add_secret
    cli.run(["vars", "generate", "--flake", str(flake.path), "machine2"])

    # Verify the secret was NOT regenerated (same value)
    new_secret = sops_store.get(generator_key, "my_secret")
    assert new_secret == original_secret, "Shared secret should not be regenerated"

    # Verify both machines now have access
    assert sops_store.machine_has_access(generator_key, "my_secret", "machine1")
    assert sops_store.machine_has_access(generator_key, "my_secret", "machine2")

    # Step 5: Add machine3 WITHOUT the shared generator - should NOT get access
    flake.machines["machine3"] = create_test_machine_config()
    # Note: machine3 does NOT have shared_generator configured
    flake.refresh()

    cli.run(["vars", "generate", "--flake", str(flake.path), "machine3"])

    # Verify machine3 does NOT have access (it doesn't use the shared generator)
    assert not sops_store.machine_has_access(generator_key, "my_secret", "machine3")
    # Verify the secret was NOT regenerated (same value)
    new_secret = sops_store.get(generator_key, "my_secret")
    assert new_secret == original_secret, "Shared secret should not be regenerated"


@pytest.mark.broken_on_darwin
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
    in_repo_store = in_repo.VarsStore(flake=flake_obj)
    sops_store = sops.SecretStore(flake=flake_obj)

    generator_not_shared = Generator(
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
    )

    initial_public = in_repo_store.get(generator_not_shared.key, "my_value").decode()
    initial_secret = sops_store.get(generator_not_shared.key, "my_secret").decode()

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
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=Shared()),
    )

    new_public = in_repo_store.get(generator_shared.key, "my_value").decode()
    new_secret = sops_store.get(generator_shared.key, "my_secret").decode()

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
    assert not sops_store.exists(generator_not_shared.key, "my_secret"), (
        "Machine-specific secret should be removed"
    )

    # Verify the new shared secret exists
    assert sops_store.exists(generator_shared.key, "my_secret"), (
        "Shared secret should exist"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_shared_generator_allows_machine_specific_differences(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that vars generation doesn't raise an error when two machines
    only differ in machine-specific fields like owner, group and mode.
    """
    flake = flake_with_sops

    machine1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_gen1 = machine1_config["clan"]["core"]["vars"]["generators"][
        "shared_generator"
    ]
    shared_gen1["share"] = True
    shared_gen1["files"]["file"]["owner"] = "root"
    shared_gen1["files"]["file"]["group"] = "root"
    shared_gen1["files"]["file"]["mode"] = "0400"
    shared_gen1["script"] = 'echo -n "secret" > "$out"/file'

    machine2_config = flake.machines["machine2"] = create_test_machine_config()
    shared_gen2 = machine2_config["clan"]["core"]["vars"]["generators"][
        "shared_generator"
    ]
    shared_gen2["share"] = True
    shared_gen2["files"]["file"]["owner"] = "user"
    shared_gen2["files"]["file"]["group"] = "wheel"
    shared_gen2["files"]["file"]["mode"] = "0440"
    shared_gen2["script"] = 'echo -n "secret" > "$out"/file'

    flake.refresh()
    monkeypatch.chdir(flake.path)

    cli.run(["vars", "generate", "--flake", str(flake.path)])

    flake_obj = Flake(str(flake.path))
    sops_store = sops.SecretStore(flake=flake_obj)

    shared_generator = Generator(
        _flake=flake_obj,
        key=GeneratorId(name="shared_generator", placement=Shared()),
    )

    assert sops_store.exists(shared_generator.key, "file")
    assert sops_store.get(shared_generator.key, "file").decode() == "secret"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generate_removes_stale_machine_symlink_when_deploy_becomes_false(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that 'vars generate' cleans up stale machine symlinks when a shared
    secret's deploy setting changes from True to False.

    Regression test: the re-encryption loop in run_generators() used to skip
    files with deploy=False entirely, so fix() was never called and stale
    machine symlinks from the deploy=True era were left behind.
    """
    flake = flake_with_sops

    # Two machines sharing a generator with deploy=True (default) + secret=True
    m1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_gen = m1_config["clan"]["core"]["vars"]["generators"]["my_shared_gen"]
    shared_gen["share"] = True
    shared_gen["files"]["my_secret"]["secret"] = True
    shared_gen["script"] = 'echo -n secret_value > "$out"/my_secret'

    m2_config = flake.machines["machine2"] = create_test_machine_config()
    m2_config["clan"]["core"]["vars"]["generators"]["my_shared_gen"] = shared_gen.copy()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Generate — both machines get access (deploy=True)
    cli.run(["vars", "generate", "--flake", str(flake.path)])

    machine1_link = (
        flake.path
        / "vars"
        / "shared"
        / "my_shared_gen"
        / "my_secret"
        / "machines"
        / "machine1"
    )
    assert machine1_link.is_symlink(), (
        "machine1 should have access after generation with deploy=True"
    )

    # Change deploy to False
    shared_gen["files"]["my_secret"]["deploy"] = False
    flake.refresh()

    # Running 'vars generate' should call fix() which removes stale symlinks
    cli.run(["vars", "generate", "--flake", str(flake.path)])

    assert not machine1_link.exists(), (
        "machine1 symlink should be removed by 'vars generate' after deploy changed to False"
    )

    # Working tree should be clean
    git_status = run(
        ["git", "status", "--porcelain", "vars/", "sops/"],
    ).stdout.strip()
    assert git_status == "", (
        f"Expected no uncommitted changes after 'vars generate', got:\n{git_status}"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_sops_fix_removes_machine_from_no_deploy_shared_secret(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that 'clan vars fix' removes and commits machine symlink deletion
    for shared secrets where deploy changed from True to False.

    This exercises the disallow_member() code path in fix(), verifying that
    the deleted symlink is included in the commit (not left as a dirty
    working tree entry).
    """
    flake = flake_with_sops

    # Step 1: Two machines sharing a generator with deploy=True (default for secret=True)
    m1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_gen = m1_config["clan"]["core"]["vars"]["generators"]["my_shared_gen"]
    shared_gen["share"] = True
    shared_gen["files"]["my_secret"]["secret"] = True
    shared_gen["script"] = 'echo -n secret_value > "$out"/my_secret'

    m2_config = flake.machines["machine2"] = create_test_machine_config()
    m2_config["clan"]["core"]["vars"]["generators"]["my_shared_gen"] = shared_gen.copy()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Step 2: Generate secrets — both machines get access (deploy=True)
    cli.run(["vars", "generate", "--flake", str(flake.path)])

    machine1_link = (
        flake.path
        / "vars"
        / "shared"
        / "my_shared_gen"
        / "my_secret"
        / "machines"
        / "machine1"
    )
    assert machine1_link.is_symlink(), (
        "machine1 should have access after generation with deploy=True"
    )

    # Step 3: Change deploy to False and refresh config
    # (shallow copy shares the nested "files" dict, so this affects both machines)
    shared_gen["files"]["my_secret"]["deploy"] = False
    flake.refresh()

    # Step 4: fix() should remove the machine symlink and commit the deletion
    cli.run(["vars", "fix", "--flake", str(flake.path), "machine1"])

    assert not machine1_link.exists(), (
        "machine1 symlink should be removed after fix with deploy=False"
    )

    # Step 5: All changes must be committed — no dirty working tree
    git_status = run(
        ["git", "status", "--porcelain", "vars/", "sops/"],
    ).stdout.strip()
    assert git_status == "", (
        f"Expected no uncommitted changes after 'clan vars fix', got:\n{git_status}"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_sops_fix_skips_add_for_no_deploy_shared_secret(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test that fix() doesn't wastefully add then remove machine access
    for shared secrets with deploy=False.

    Without the optimization, fix() calls add_secret() (creating an individual
    commit like 'vars: add machine1 to secret ...') then immediately removes
    the symlink via disallow_member(). This is a no-op with extra commits.
    """
    flake = flake_with_sops

    # Shared generator with deploy=False from the start
    m1_config = flake.machines["machine1"] = create_test_machine_config()
    shared_gen = m1_config["clan"]["core"]["vars"]["generators"]["my_shared_gen"]
    shared_gen["share"] = True
    shared_gen["files"]["my_secret"]["secret"] = True
    shared_gen["files"]["my_secret"]["deploy"] = False
    shared_gen["script"] = 'echo -n secret_value > "$out"/my_secret'

    m2_config = flake.machines["machine2"] = create_test_machine_config()
    m2_config["clan"]["core"]["vars"]["generators"]["my_shared_gen"] = shared_gen.copy()

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # Generate secrets (no machine symlink since deploy=False)
    cli.run(["vars", "generate", "--flake", str(flake.path)])

    machine1_link = (
        flake.path
        / "vars"
        / "shared"
        / "my_shared_gen"
        / "my_secret"
        / "machines"
        / "machine1"
    )
    assert not machine1_link.exists(), (
        "machine1 should NOT have access after generation with deploy=False"
    )

    # Record HEAD before fix
    head_before = run(["git", "rev-parse", "HEAD"]).stdout.strip()

    # Run fix
    cli.run(["vars", "fix", "--flake", str(flake.path), "machine1"])

    # fix() should NOT create intermediate "vars: add" commits
    fix_commits = run(
        ["git", "log", f"{head_before}..HEAD", "--pretty=%s"],
    ).stdout.strip()
    assert "vars: add" not in fix_commits, (
        f"fix() should not wastefully add machine access for shared non-deploy secrets.\n"
        f"Commits created by fix:\n{fix_commits}"
    )

    # Machine should still not have access
    assert not machine1_link.exists(), (
        "machine1 should still not have access after fix with deploy=False"
    )

    # Working tree should be clean
    git_status = run(
        ["git", "status", "--porcelain", "vars/", "sops/"],
    ).stdout.strip()
    assert git_status == "", (
        f"Expected no uncommitted changes after 'clan vars fix', got:\n{git_status}"
    )
