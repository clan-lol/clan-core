import json
import tempfile
from pathlib import Path
from typing import Any

import pytest
from cli import Cli

from clan_cli import config
from clan_cli.config import parsing

example_options = f"{Path(config.__file__).parent}/jsonschema/options.json"


# use pytest.parametrize
@pytest.mark.parametrize(
    "args,expected",
    [
        (["name", "DavHau"], {"name": "DavHau"}),
        (
            ["kernelModules", "foo", "bar", "baz"],
            {"kernelModules": ["foo", "bar", "baz"]},
        ),
        (["services.opt", "test"], {"services": {"opt": "test"}}),
        (["userIds.DavHau", "42"], {"userIds": {"DavHau": 42}}),
    ],
)
def test_set_some_option(
    args: list[str],
    expected: dict[str, Any],
    test_flake: Path,
) -> None:
    # create temporary file for out_file
    with tempfile.NamedTemporaryFile() as out_file:
        with open(out_file.name, "w") as f:
            json.dump({}, f)
        cli = Cli()
        cli.run(
            [
                "config",
                "--quiet",
                "--options-file",
                example_options,
                "--settings-file",
                out_file.name,
            ]
            + args
        )
        json_out = json.loads(open(out_file.name).read())
        assert json_out == expected


def test_configure_machine(
    test_flake: Path,
    temporary_dir: Path,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HOME", str(temporary_dir))
    cli = Cli()
    cli.run(["config", "-m", "machine1", "clan.jitsi.enable", "true"])
    # clear the output buffer
    capsys.readouterr()
    # read a option value
    cli.run(["config", "-m", "machine1", "clan.jitsi.enable"])
    # read the output
    assert capsys.readouterr().out == "true\n"


def test_walk_jsonschema_all_types() -> None:
    schema = dict(
        type="object",
        properties=dict(
            array=dict(
                type="array",
                items=dict(
                    type="string",
                ),
            ),
            boolean=dict(type="boolean"),
            integer=dict(type="integer"),
            number=dict(type="number"),
            string=dict(type="string"),
        ),
    )
    expected = {
        "array": list[str],
        "boolean": bool,
        "integer": int,
        "number": float,
        "string": str,
    }
    assert config.parsing.options_types_from_schema(schema) == expected


def test_walk_jsonschema_nested() -> None:
    schema = dict(
        type="object",
        properties=dict(
            name=dict(
                type="object",
                properties=dict(
                    first=dict(type="string"),
                    last=dict(type="string"),
                ),
            ),
            age=dict(type="integer"),
        ),
    )
    expected = {
        "age": int,
        "name.first": str,
        "name.last": str,
    }
    assert config.parsing.options_types_from_schema(schema) == expected


# test walk_jsonschema with dynamic attributes (e.g. "additionalProperties")
def test_walk_jsonschema_dynamic_attrs() -> None:
    schema = dict(
        type="object",
        properties=dict(
            age=dict(type="integer"),
            users=dict(
                type="object",
                additionalProperties=dict(type="string"),
            ),
        ),
    )
    expected = {
        "age": int,
        "users.<name>": str,  # <name> is a placeholder for any string
    }
    assert config.parsing.options_types_from_schema(schema) == expected


def test_type_from_schema_path_simple() -> None:
    schema = dict(
        type="boolean",
    )
    assert parsing.type_from_schema_path(schema, []) == bool


def test_type_from_schema_path_nested() -> None:
    schema = dict(
        type="object",
        properties=dict(
            name=dict(
                type="object",
                properties=dict(
                    first=dict(type="string"),
                    last=dict(type="string"),
                ),
            ),
            age=dict(type="integer"),
        ),
    )
    assert parsing.type_from_schema_path(schema, ["age"]) == int
    assert parsing.type_from_schema_path(schema, ["name", "first"]) == str


def test_type_from_schema_path_dynamic_attrs() -> None:
    schema = dict(
        type="object",
        properties=dict(
            age=dict(type="integer"),
            users=dict(
                type="object",
                additionalProperties=dict(type="string"),
            ),
        ),
    )
    assert parsing.type_from_schema_path(schema, ["age"]) == int
    assert parsing.type_from_schema_path(schema, ["users", "foo"]) == str


# test the cast function with simple types
def test_cast_simple() -> None:
    assert config.cast(["true"], bool, "foo-option") is True
