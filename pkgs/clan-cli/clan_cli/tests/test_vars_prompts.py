import logging
import os
import sys
from pathlib import Path

import pexpect  # type: ignore[import-untyped]
import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config
from clan_cli.tests.helpers import cli
from clan_cli.vars.public_modules import in_repo
from clan_cli.vars.secret_modules import sops
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.vars._types import GeneratorId, PerMachine
from clan_lib.vars.generate import (
    GeneratorPromptIdentifier,
    get_generator_prompt_previous_values,
    get_generators,
    run_generators,
)
from clan_lib.vars.generator import (
    Generator,
)


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_prompt(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
    caplog: pytest.LogCaptureFixture,
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
        "clan_lib.vars.prompt.MOCK_PROMPT_RESPONSE",
        iter(["line input", "my\nmultiline\ninput\n", "prompt_persist"]),
    )

    # Run the generator which will collect prompts and generate vars
    with caplog.at_level(logging.INFO):
        cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])

    # Verify that the prompt log messages include machine names
    assert (
        "Prompting value for my_generator/prompt1 for machines: my_machine"
        in caplog.text
    )
    assert (
        "Prompting value for my_generator/prompt2 for machines: my_machine"
        in caplog.text
    )
    assert (
        "Prompting value for my_generator/prompt_persist for machines: my_machine"
        in caplog.text
    )

    # Set up objects for testing the results
    flake_obj = Flake(str(flake.path))
    my_generator = Generator(
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
    )
    my_generator_with_details = Generator(
        files=[],
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
    )

    # Verify that non-persistent prompts created public vars correctly
    in_repo_store = in_repo.VarsStore(flake=flake_obj)
    assert in_repo_store.exists(my_generator.key, "line_value")
    assert in_repo_store.get(my_generator.key, "line_value").decode() == "line input"

    assert in_repo_store.exists(my_generator.key, "multiline_value")
    assert (
        in_repo_store.get(my_generator.key, "multiline_value").decode()
        == "my\nmultiline\ninput\n"
    )

    # Verify that persistent prompt was stored as a secret
    sops_store = sops.SecretStore(flake=flake_obj)
    assert sops_store.exists(my_generator_with_details.key, "prompt_persist")
    assert (
        sops_store.get(my_generator.key, "prompt_persist").decode() == "prompt_persist"
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_prompt_prefill_on_regeneration(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test prompt handling: pre-fill, editing, arrow key handling, and auto-accept.

    This test covers:
    1. Pre-filling existing prompts with previous values on regeneration
    2. Keeping previous values by pressing Enter
    3. Editing values with backspace (including across newlines in multiline)
    4. Arrow keys being ignored (not breaking input)
    5. Auto-accepting existing prompts when running without --regenerate

    Test flow:
    - First gen: Enter initial values for prompt1, secret_prompt, multiline_prompt
    - Second gen (--regenerate): Add prompt2, test multiline backspace across newlines
    - Third gen (--regenerate): Test editing prompt1 with backspace
    - Fourth gen (NO --regenerate): Add prompt3, verify auto-accept of existing prompts
    """
    flake = flake_with_sops
    # Add clan_cli's parent to PYTHONPATH so subprocess can find it
    clan_cli_path = Path(__file__).parent.parent.parent  # pkgs/clan-cli
    spawn_env = os.environ.copy()
    spawn_env["PYTHONPATH"] = str(clan_cli_path)

    # Configure the machine and generator with one prompt initially
    config = flake.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]

    # Configure first prompt - persisted so it can be re-used
    my_generator["prompts"]["10_prompt1"]["description"] = "First prompt"
    my_generator["prompts"]["10_prompt1"]["persist"] = True
    my_generator["prompts"]["10_prompt1"]["type"] = "line"
    my_generator["files"]["10_prompt1"]["secret"] = False

    # Configure a secret prompt (starts as single-line hidden)
    my_generator["prompts"]["20_secret_prompt"]["description"] = "Secret value"
    my_generator["prompts"]["20_secret_prompt"]["persist"] = True
    my_generator["prompts"]["20_secret_prompt"]["type"] = "hidden"
    my_generator["files"]["20_secret_prompt"]["secret"] = True

    # Configure a multiline prompt for testing backspace across newlines
    my_generator["prompts"]["30_multiline_prompt"]["description"] = "Multiline input"
    my_generator["prompts"]["30_multiline_prompt"]["persist"] = True
    my_generator["prompts"]["30_multiline_prompt"]["type"] = "multiline"
    my_generator["files"]["30_multiline_prompt"]["secret"] = False

    flake.refresh()
    monkeypatch.chdir(flake.path)

    # First generation: provide initial values
    child = pexpect.spawn(
        sys.executable,
        [
            "-m",
            "clan_cli",
            "vars",
            "generate",
            "--flake",
            str(flake.path),
            "my_machine",
        ],
        timeout=30,
        encoding="utf-8",
        env=spawn_env,
    )
    child.expect("First prompt:")
    child.sendline("initial_value")
    # Secret prompt requires confirmation (enter twice)
    child.expect("Secret value")
    child.sendline("secret123")
    child.expect("Confirm")
    child.sendline("secret123")
    # Multiline prompt - enter two lines with arrow keys interspersed (should be ignored)
    # Arrow key escape sequences: Up=\x1b[A, Down=\x1b[B, Right=\x1b[C, Left=\x1b[D
    child.expect("Multiline input")
    child.send("li")
    child.send("\x1b[A")  # Up arrow - should be ignored
    child.send("ne")
    child.send("\x1b[D")  # Left arrow - should be ignored
    child.sendline("1")  # Complete "line1" and press Enter
    child.send("\x1b[B")  # Down arrow - should be ignored
    child.send("line")
    child.send("\x1b[C")  # Right arrow - should be ignored
    child.send("2")
    child.send("\x04")  # Ctrl-D to finish
    child.expect(pexpect.EOF)
    child.close()
    assert child.exitstatus == 0, f"First generation failed: {child.before}"

    # Verify initial generation worked
    flake_obj = Flake(str(flake.path))
    in_repo_store = in_repo.VarsStore(flake=flake_obj)
    sops_store = sops.SecretStore(flake=flake_obj)
    generator = Generator(
        _flake=flake_obj,
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
    )
    assert in_repo_store.get(generator.key, "10_prompt1").decode() == "initial_value"
    assert sops_store.get(generator.key, "20_secret_prompt").decode() == "secret123"
    assert (
        in_repo_store.get(generator.key, "30_multiline_prompt").decode()
        == "line1\nline2"
    )

    # Now extend the generator with a second prompt and change secret to multiline
    my_generator["prompts"]["15_prompt2"]["description"] = "Second prompt"
    my_generator["prompts"]["15_prompt2"]["persist"] = True
    my_generator["prompts"]["15_prompt2"]["type"] = "line"
    my_generator["files"]["15_prompt2"]["secret"] = False
    # Change 20_secret_prompt to multiline-hidden
    my_generator["prompts"]["20_secret_prompt"]["type"] = "multiline-hidden"
    flake.refresh()

    # Second generation:
    # - prompt1: press Enter to accept the pre-filled value
    # - prompt2: type new value
    # - secret_prompt: now multiline-hidden, enter multiple lines + Ctrl-D, then confirm
    child = pexpect.spawn(
        sys.executable,
        [
            "-m",
            "clan_cli",
            "vars",
            "generate",
            "--flake",
            str(flake.path),
            "my_machine",
            "--regenerate",
        ],
        timeout=30,
        encoding="utf-8",
        env=spawn_env,
    )
    # First prompt should show pre-filled value, just press Enter
    child.expect("First prompt:")
    child.sendline("")  # Press Enter to keep pre-filled value
    # Second prompt needs new value
    child.expect("Second prompt:")
    child.sendline("second_value")
    # Secret prompt is now multiline-hidden, enter new multiline value
    child.expect("Enter multiple lines")
    child.sendline("secret_line1")
    child.sendline("secret_line2")
    child.send("\x04")  # Ctrl-D to finish first input
    child.expect("Confirm")
    child.sendline("secret_line1")
    child.sendline("secret_line2")
    child.send("\x04")  # Ctrl-D to finish confirmation
    # Multiline prompt - test backspace across newlines
    # Pre-filled: "line1\nline2" (cursor at end of "line2")
    # Backspace 6 times: delete "line2" (5 chars) + newline (1 char)
    child.expect("Multiline input")
    child.send("\x7f" * 6)  # DEL to delete "line2" + newline
    child.sendline("modified")  # Type new text
    child.send("\x04")  # Ctrl-D to finish
    child.expect(pexpect.EOF)
    child.close()
    assert child.exitstatus == 0, f"Second generation failed: {child.before}"

    # Verify that the first prompt value is preserved (user pressed enter on prefilled)
    assert in_repo_store.get(generator.key, "10_prompt1").decode() == "initial_value", (
        "First prompt value should be preserved when user presses enter"
    )

    # Verify that the second prompt has the new value
    assert in_repo_store.get(generator.key, "15_prompt2").decode() == "second_value", (
        "Second prompt should have the newly entered value"
    )

    # Verify multiline secret value
    assert (
        sops_store.get(generator.key, "20_secret_prompt").decode()
        == "secret_line1\nsecret_line2"
    ), "Secret prompt should have multiline value"

    # Verify backspace across newlines worked in multiline prompt
    assert (
        in_repo_store.get(generator.key, "30_multiline_prompt").decode()
        == "line1modified"
    ), "Backspace should be able to delete across newline boundaries in multiline input"

    # Third generation:
    # - prompt1: delete pre-filled value with backspace and enter new value
    # - prompt2: press Enter to keep pre-filled value
    # - secret_prompt: multiline-hidden, Ctrl-D to keep previous value
    child = pexpect.spawn(
        sys.executable,
        [
            "-m",
            "clan_cli",
            "vars",
            "generate",
            "--flake",
            str(flake.path),
            "my_machine",
            "--regenerate",
        ],
        timeout=30,
        encoding="utf-8",
        env=spawn_env,
    )
    # First prompt has "initial_value" pre-filled - delete it with backspaces and type new
    child.expect("First prompt:")
    # Send backspaces to delete "initial_value" (13 characters)
    child.send("\x7f" * 13)  # DEL character (ASCII 127)
    child.sendline("modified_value")
    # Second prompt has "second_value" pre-filled, just press Enter to keep it
    child.expect("Second prompt:")
    child.sendline("")
    # Secret prompt (multiline-hidden) shows marker, Ctrl-D to keep previous value
    child.expect("Enter multiple lines")
    child.send("\x04")  # Ctrl-D to keep previous value
    # Multiline prompt - keep previous value
    child.expect("Multiline input")
    child.send("\x04")  # Ctrl-D to keep previous value
    child.expect(pexpect.EOF)
    child.close()
    assert child.exitstatus == 0, f"Third generation failed: {child.before}"

    # Verify that the first prompt value was changed
    assert (
        in_repo_store.get(generator.key, "10_prompt1").decode() == "modified_value"
    ), "First prompt value should be modified after backspace and new input"

    # Verify that the second prompt value is preserved
    assert in_repo_store.get(generator.key, "15_prompt2").decode() == "second_value", (
        "Second prompt value should be preserved when user presses enter"
    )

    # Verify multiline secret value is preserved
    assert (
        sops_store.get(generator.key, "20_secret_prompt").decode()
        == "secret_line1\nsecret_line2"
    ), "Secret prompt multiline value should be preserved when user presses Ctrl-D"

    # Fourth generation: Test auto-accept without --regenerate
    # Add a new prompt to trigger regeneration, but run WITHOUT --regenerate
    # Existing prompts should be auto-accepted, only new prompt should be asked
    my_generator["prompts"]["25_prompt3"]["description"] = "Third prompt"
    my_generator["prompts"]["25_prompt3"]["persist"] = True
    my_generator["prompts"]["25_prompt3"]["type"] = "line"
    my_generator["files"]["25_prompt3"]["secret"] = False
    flake.refresh()

    child = pexpect.spawn(
        sys.executable,
        [
            "-m",
            "clan_cli",
            "vars",
            "generate",
            "--flake",
            str(flake.path),
            "my_machine",
            # Note: no --regenerate flag - existing prompts should be auto-accepted
        ],
        timeout=30,
        encoding="utf-8",
        env=spawn_env,
    )
    # Should NOT prompt for existing prompts - only for the new third prompt
    child.expect("Third prompt:")
    child.sendline("third_value")
    child.expect(pexpect.EOF)
    child.close()
    assert child.exitstatus == 0, f"Fourth generation failed: {child.before}"

    # Verify existing values are preserved (auto-accepted)
    assert (
        in_repo_store.get(generator.key, "10_prompt1").decode() == "modified_value"
    ), "First prompt should be auto-accepted without --regenerate"
    assert in_repo_store.get(generator.key, "15_prompt2").decode() == "second_value", (
        "Second prompt should be auto-accepted without --regenerate"
    )
    # Verify new prompt value was set
    assert in_repo_store.get(generator.key, "25_prompt3").decode() == "third_value", (
        "Third prompt should have the newly entered value"
    )


@pytest.mark.broken_on_darwin
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
    store = in_repo.VarsStore(machine.flake)
    my_generator = Generator(
        _flake=machine.flake,
        key=GeneratorId(name="my_generator", placement=PerMachine("my_machine")),
    )
    assert store.exists(my_generator.key, "prompt1")
    assert store.get(my_generator.key, "prompt1").decode() == "input1"
    run_generators(
        machines=[Machine(name="my_machine", flake=Flake(str(flake.path)))],
        generators=["my_generator"],
        prompt_values={
            "my_generator": {
                "prompt1": "input2",
            },
        },
    )
    assert store.get(my_generator.key, "prompt1").decode() == "input2"

    machine = Machine(name="my_machine", flake=Flake(str(flake.path)))
    generators = get_generators(
        machines=[machine],
        full_closure=True,
    )
    # get_generators should bind the store
    assert generators[0].files[0]._store is not None

    assert len(generators) == 1
    assert generators[0].name == "my_generator"
    assert generators[0].prompts[0].name == "prompt1"
    assert generators[0].get_previous_value(generators[0].prompts[0]) == "input2"


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_generator_prompt_previous_values(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: ClanFlake,
) -> None:
    """Test the get_generator_prompt_previous_values API endpoint."""
    flake_ = flake_with_sops

    config = flake_.machines["my_machine"] = create_test_machine_config()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["prompts"]["prompt1"]["persist"] = True
    my_generator["script"] = 'cat "$prompts"/prompt1 > "$out"/my_value'
    flake_.refresh()
    monkeypatch.chdir(flake_.path)

    # First run to store a value
    run_generators(
        machines=[Machine(name="my_machine", flake=Flake(str(flake_.path)))],
        generators=["my_generator"],
        prompt_values={
            "my_generator": {
                "prompt1": "test_value",
            },
        },
    )

    machine = Machine(name="my_machine", flake=Flake(str(flake_.path)))

    # Test fetching existing value
    results = get_generator_prompt_previous_values(
        machine=machine,
        prompt_identifiers=[
            GeneratorPromptIdentifier(
                generator_name="my_generator", prompt_name="prompt1"
            ),
        ],
    )
    assert len(results) == 1
    assert results[0].generator_name == "my_generator"
    assert results[0].prompt_name == "prompt1"
    assert results[0].value == "test_value"

    # Test error on non-existent generator
    with pytest.raises(ClanError, match="Generator 'nonexistent' not found"):
        get_generator_prompt_previous_values(
            machine=machine,
            prompt_identifiers=[
                GeneratorPromptIdentifier(
                    generator_name="nonexistent", prompt_name="prompt1"
                ),
            ],
        )

    # Test error on non-existent prompt
    with pytest.raises(ClanError, match="Prompt 'nonexistent' not found"):
        get_generator_prompt_previous_values(
            machine=machine,
            prompt_identifiers=[
                GeneratorPromptIdentifier(
                    generator_name="my_generator", prompt_name="nonexistent"
                ),
            ],
        )
