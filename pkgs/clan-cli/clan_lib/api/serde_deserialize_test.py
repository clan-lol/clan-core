from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal, TypedDict

import pytest

# Functions to test
from clan_lib.api import dataclass_to_dict, from_dict
from clan_lib.api.serde import is_type_in_union
from clan_lib.errors import ClanError
from clan_lib.machines import machines


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
        home: Path | str | None
        age: Age
        age_list: list[Age]
        age_dict: dict[str, Age]
        # Optional field

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


def test_nested_nullable() -> None:
    @dataclass
    class SystemConfig:
        language: str | None = field(default=None)
        keymap: str | None = field(default=None)
        ssh_keys_path: list[str] | None = field(default=None)

    @dataclass
    class FlashOptions:
        machine: machines.Machine
        mode: str
        disks: dict[str, str]
        system_config: SystemConfig
        dry_run: bool
        write_efi_boot_entries: bool
        debug: bool

    data = {
        "machine": {
            "name": "flash-installer",
            "flake": {"identifier": "git+https://git.clan.lol/clan/clan-core"},
        },
        "mode": "format",
        "disks": {"main": "/dev/sda"},
        "system_config": {"language": "en_US.UTF-8", "keymap": "en"},
        "dry_run": False,
        "write_efi_boot_entries": False,
        "debug": False,
        "op_key": "jWnTSHwYhSgr7Qz3u4ppD",
    }

    expected = FlashOptions(
        machine=machines.Machine(
            name="flash-installer",
            flake=machines.Flake("git+https://git.clan.lol/clan/clan-core"),
        ),
        mode="format",
        disks={"main": "/dev/sda"},
        system_config=SystemConfig(
            language="en_US.UTF-8",
            keymap="en",
            ssh_keys_path=None,
        ),
        dry_run=False,
        write_efi_boot_entries=False,
        debug=False,
    )

    assert from_dict(FlashOptions, data) == expected


def test_simple_field_missing() -> None:
    @dataclass
    class Person:
        name: str

    person_dict: Any = {}

    with pytest.raises(ClanError):
        from_dict(Person, person_dict)


def test_nullable() -> None:
    @dataclass
    class Person:
        name: None

    person_dict = {
        "name": None,
    }

    from_dict(Person, person_dict)


def test_nullable_non_exist() -> None:
    @dataclass
    class Person:
        name: None

    person_dict: Any = {}

    with pytest.raises(ClanError):
        from_dict(Person, person_dict)


def test_list() -> None:
    data = [
        {"name": "John"},
        {"name": "Sarah"},
    ]

    @dataclass
    class Name:
        name: str

    result = from_dict(list[Name], data)

    assert result == [Name("John"), Name("Sarah")]


def test_alias_field() -> None:
    @dataclass
    class Person:
        name: str = field(metadata={"alias": "--user-name--"})

    data = {"--user-name--": "John"}
    expected = Person(name="John")

    person = from_dict(Person, data)

    # Deserialize
    assert person == expected

    # Serialize with alias
    assert dataclass_to_dict(person) == data

    # Serialize without alias
    assert dataclass_to_dict(person, use_alias=False) == {"name": "John"}


def test_alias_field_from_orig_name() -> None:
    """Field declares an alias. But the data is provided with the field name."""

    @dataclass
    class Person:
        name: str = field(metadata={"alias": "--user-name--"})

    data = {"user": "John"}

    with pytest.raises(ClanError):
        from_dict(Person, data)


def test_none_or_string() -> None:
    """Field declares an alias. But the data is provided with the field name."""
    data = None

    @dataclass
    class Person:
        name: Path

    checked: str | None = from_dict(str | None, data)
    assert checked is None

    checked2: dict[str, str] | None = from_dict(dict[str, str] | None, data)
    assert checked2 is None

    checked3: Person | None = from_dict(Person | None, data)
    assert checked3 is None


def test_union_with_none_edge_cases() -> None:
    """Test various union types with None to ensure issubclass() error is avoided.
    This specifically tests the fix for the TypeError in is_type_in_union.
    """
    # Test basic types with None
    assert from_dict(str | None, None) is None
    assert from_dict(str | None, "hello") == "hello"

    # Test dict with None - this was the specific case that failed
    assert from_dict(dict[str, str] | None, None) is None
    assert from_dict(dict[str, str] | None, {"key": "value"}) == {"key": "value"}

    # Test list with None
    assert from_dict(list[str] | None, None) is None
    assert from_dict(list[str] | None, ["a", "b"]) == ["a", "b"]

    # Test dataclass with None
    @dataclass
    class TestClass:
        value: str

    assert from_dict(TestClass | None, None) is None
    assert from_dict(TestClass | None, {"value": "test"}) == TestClass(value="test")

    # Test Path with None (since it's used in the original failing test)
    assert from_dict(Path | None, None) is None
    assert from_dict(Path | None, "/home/test") == Path("/home/test")

    # Test that the is_type_in_union function works correctly
    # This is the core of what was fixed - ensuring None doesn't cause issubclass error
    # These should not raise TypeError anymore
    assert is_type_in_union(str | None, type(None)) is True
    assert is_type_in_union(dict[str, str] | None, type(None)) is True
    assert is_type_in_union(list[str] | None, type(None)) is True
    assert is_type_in_union(Path | None, type(None)) is True


def test_roundtrip_escape() -> None:
    assert from_dict(str, "\n") == "\n"
    assert dataclass_to_dict("\n") == "\n"

    # Test that the functions are inverses of each other
    # f(g(x)) == x
    # and
    # g(f(x)) == x
    assert from_dict(str, dataclass_to_dict("\n")) == "\n"
    assert dataclass_to_dict(from_dict(str, "\\n")) == "\\n"


def test_roundtrip_typed_dict() -> None:
    class Person(TypedDict):
        name: str

    data = {"name": "John"}
    person = Person(name="John")

    # Check that the functions are the inverses of each other
    # f(g(x)) == x
    # and
    # g(f(x)) == x
    assert from_dict(Person, dataclass_to_dict(person)) == person
    assert dataclass_to_dict(from_dict(Person, data)) == person


def test_construct_typed_dict() -> None:
    class Person(TypedDict):
        name: str

    data = {"name": "John"}
    person = Person(name="John")

    # Check that the from_dict function works with TypedDict
    assert from_dict(Person, data) == person

    with pytest.raises(ClanError):
        # Not a valid value
        from_dict(Person, None)


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


def test_literal_field() -> None:
    @dataclass
    class Person:
        name: Literal["get_system_file", "select_folder", "save"]

    data = {"name": "get_system_file"}
    expected = Person(name="get_system_file")
    assert from_dict(Person, data) == expected

    assert dataclass_to_dict(expected) == data

    with pytest.raises(ClanError):
        # Not a valid value
        from_dict(Person, {"name": "open"})


def test_enum_roundtrip() -> None:
    class MyEnum(Enum):
        FOO = "abc"
        BAR = 2

    @dataclass
    class Person:
        name: MyEnum

    # Both are equivalent
    data = {"name": "abc"}  # JSON Representation
    expected = Person(name=MyEnum.FOO)  # Data representation

    assert from_dict(Person, data) == expected

    assert dataclass_to_dict(expected) == data

    # Same test for integer values
    data2 = {"name": 2}  # JSON Representation
    expected2 = Person(name=MyEnum.BAR)  # Data representation

    assert from_dict(Person, data2) == expected2

    assert dataclass_to_dict(expected2) == data2


# for the test below
# we would import this from the nix_models
class Unknown:
    pass


def test_unknown_deserialize() -> None:
    @dataclass
    class Person:
        name: Unknown

    data = {"name": ["a", "b"]}

    person = from_dict(Person, data)
    person.name = ["a", "b"]


def test_unknown_serialize() -> None:
    @dataclass
    class Person:
        name: Unknown

    data = Person(["a", "b"])  # type: ignore[arg-type]

    person = dataclass_to_dict(data)
    assert person == {"name": ["a", "b"]}


def test_union_dataclass() -> None:
    @dataclass
    class A:
        val: str | list[str] | None = None

    data1 = {"val": "hello"}
    expected1 = A(val="hello")
    assert from_dict(A, data1) == expected1
    data2 = {"val": ["a", "b"]}
    expected2 = A(val=["a", "b"])
    assert from_dict(A, data2) == expected2
    data3 = {"val": None}
    expected3 = A(val=None)
    assert from_dict(A, data3) == expected3
    data4: dict[str, object] = {}
    expected4 = A(val=None)
    assert from_dict(A, data4) == expected4
