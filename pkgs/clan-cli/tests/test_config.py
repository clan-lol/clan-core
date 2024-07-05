from pathlib import Path

import pytest
from fixtures_flakes import FlakeForTest
from helpers.cli import Cli

from clan_cli import config
from clan_cli.config import parsing
from clan_cli.errors import ClanError

example_options = f"{Path(config.__file__).parent}/jsonschema/options.json"


def test_configure_machine(
    test_flake: FlakeForTest,
    temporary_home: Path,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cli = Cli()

    # clear the output buffer
    capsys.readouterr()
    # read a option value
    cli.run(
        [
            "config",
            "--flake",
            str(test_flake.path),
            "-m",
            "machine1",
            "clan.jitsi.enable",
        ]
    )

    # read the output
    assert capsys.readouterr().out == "false\n"


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


def test_map_type() -> None:
    with pytest.raises(ClanError):
        config.map_type("foo")
    assert config.map_type("string") == str
    assert config.map_type("integer") == int
    assert config.map_type("boolean") == bool
    assert config.map_type("attribute set of string") == dict[str, str]
    assert config.map_type("attribute set of integer") == dict[str, int]
    assert config.map_type("null or string") == str | None


# test the cast function with simple types
def test_cast() -> None:
    assert (
        config.cast(value=["true"], input_type=bool, opt_description="foo-option")
        is True
    )
    assert (
        config.cast(value=["null"], input_type=str | None, opt_description="foo-option")
        is None
    )
    assert (
        config.cast(value=["bar"], input_type=str | None, opt_description="foo-option")
        == "bar"
    )


@pytest.mark.parametrize(
    "option,value,options,expected",
    [
        ("foo.bar", ["baz"], {"foo.bar": {"type": "str"}}, ("foo.bar", ["baz"])),
        ("foo.bar", ["baz"], {"foo": {"type": "attrs"}}, ("foo", {"bar": ["baz"]})),
        (
            "users.users.my-user.name",
            ["my-name"],
            {"users.users.<name>.name": {"type": "str"}},
            ("users.users.<name>.name", ["my-name"]),
        ),
        (
            "foo.bar.baz.bum",
            ["val"],
            {"foo.<name>.baz": {"type": "attrs"}},
            ("foo.<name>.baz", {"bum": ["val"]}),
        ),
        (
            "userIds.DavHau",
            ["42"],
            {"userIds": {"type": "attrs"}},
            ("userIds", {"DavHau": ["42"]}),
        ),
    ],
)
def test_find_option(option: str, value: list, options: dict, expected: tuple) -> None:
    assert config.find_option(option, value, options) == expected
