import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.vars.generate import (
    run_generators,
)


@pytest.mark.broken_on_darwin
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


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generator_script_missing_output_file(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure a clear error when a generator script doesn't produce a declared output file."""
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["expected_file"]["secret"] = False
    # Script writes to wrong filename
    my_generator["script"] = 'echo "hello" > "$out"/wrong_file'
    flake.refresh()
    monkeypatch.chdir(flake.path)
    with pytest.raises(
        ClanError,
        match="did not generate a file for 'expected_file'",
    ):
        cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_generator_script_fails_with_nonzero_exit(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure a clear error when a generator script exits with a non-zero status."""
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = 'echo "failing" >&2; exit 1'
    flake.refresh()
    monkeypatch.chdir(flake.path)
    with pytest.raises(ClanError):
        cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_circular_dependency_raises_error(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Ensure that circular dependencies between generators are caught."""
    flake = flake_with_sops

    config = flake.machines["my_machine"] = create_test_machine_config()
    gen_a = config["clan"]["core"]["vars"]["generators"]["gen_a"]
    gen_a["files"]["value_a"]["secret"] = False
    gen_a["script"] = 'echo "a" > "$out"/value_a'
    gen_a["dependencies"] = ["gen_b"]

    gen_b = config["clan"]["core"]["vars"]["generators"]["gen_b"]
    gen_b["files"]["value_b"]["secret"] = False
    gen_b["script"] = 'echo "b" > "$out"/value_b'
    gen_b["dependencies"] = ["gen_a"]

    flake.refresh()
    monkeypatch.chdir(flake.path)
    with pytest.raises(Exception, match="cycle"):
        cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])


@pytest.mark.broken_on_darwin
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


@pytest.mark.broken_on_darwin
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
            generators=[generator],
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
                    generators=[generator],
                )
        else:
            run_generators(
                machines=[Machine(name="my_machine", flake=Flake(str(flake.path)))],
                generators=[generator],
            )


@pytest.mark.broken_on_darwin
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
