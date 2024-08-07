from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Functions to test
from clan_cli.api import (
    dataclass_to_dict,
    from_dict,
)
from clan_cli.errors import ClanError
from clan_cli.inventory import (
    Inventory,
    Machine,
    MachineDeploy,
    Meta,
    Service,
    ServiceBorgbackup,
    ServiceBorgbackupRole,
    ServiceBorgbackupRoleClient,
    ServiceBorgbackupRoleServer,
    ServiceMeta,
)


def test_simple() -> None:
    @dataclass
    class Person:
        name: str

    person_dict = {
        "name": "John",
    }

    expected_person = Person(
        name="John",
    )

    assert from_dict(Person, person_dict) == expected_person


def test_nested() -> None:
    @dataclass
    class Age:
        value: str

    @dataclass
    class Person:
        name: str
        # deeply nested dataclasses
        age: Age
        age_list: list[Age]
        age_dict: dict[str, Age]
        # Optional field
        home: Path | None

    person_dict = {
        "name": "John",
        "age": {
            "value": "99",
        },
        "age_list": [{"value": "66"}, {"value": "77"}],
        "age_dict": {"now": {"value": "55"}, "max": {"value": "100"}},
        "home": "/home",
    }

    expected_person = Person(
        name="John",
        age=Age("99"),
        age_list=[Age("66"), Age("77")],
        age_dict={"now": Age("55"), "max": Age("100")},
        home=Path("/home"),
    )

    assert from_dict(Person, person_dict) == expected_person


def test_simple_field_missing() -> None:
    @dataclass
    class Person:
        name: str

    person_dict = {}

    with pytest.raises(ClanError):
        from_dict(Person, person_dict)


def test_deserialize_extensive_inventory() -> None:
    data = {
        "meta": {"name": "superclan", "description": "nice clan"},
        "services": {
            "borgbackup": {
                "instance1": {
                    "meta": {
                        "name": "borg1",
                    },
                    "roles": {
                        "client": {},
                        "server": {},
                    },
                }
            },
        },
        "machines": {"foo": {"name": "foo", "deploy": {}}},
    }
    expected = Inventory(
        meta=Meta(name="superclan", description="nice clan"),
        services=Service(
            borgbackup={
                "instance1": ServiceBorgbackup(
                    meta=ServiceMeta(name="borg1"),
                    roles=ServiceBorgbackupRole(
                        client=ServiceBorgbackupRoleClient(),
                        server=ServiceBorgbackupRoleServer(),
                    ),
                )
            }
        ),
        machines={"foo": Machine(deploy=MachineDeploy(), name="foo")},
    )
    assert from_dict(Inventory, data) == expected


def test_alias_field() -> None:
    @dataclass
    class Person:
        name: str = field(metadata={"alias": "--user-name--"})

    data = {"--user-name--": "John"}
    expected = Person(name="John")

    assert from_dict(Person, data) == expected


def test_path_field() -> None:
    @dataclass
    class Person:
        name: Path

    data = {"name": "John"}
    expected = Person(name=Path("John"))

    assert from_dict(Person, data) == expected


def test_private_public_fields() -> None:
    @dataclass
    class Person:
        name: Path
        _name: str | None = None

    data = {"name": "John"}
    expected = Person(name=Path("John"))
    assert from_dict(Person, data) == expected

    assert dataclass_to_dict(expected) == data
