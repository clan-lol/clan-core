# mypy: disable-error-code="var-annotated"

import json
from pathlib import Path
from typing import Any

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_lib.cmd import run
from clan_lib.flake import Flake
from clan_lib.git import commit_file
from clan_lib.locked_open import locked_open
from clan_lib.nix import nix_command
from clan_lib.templates import (
    ClanExports,
    InputName,
    TemplateName,
    copy_from_nixstore,
    get_clan_nix_attrset,
    get_template,
    list_templates,
)


# Function to write clan attributes to a file
def write_clan_attr(clan_attrset: dict[str, Any], flake: FlakeForTest) -> None:
    file = flake.path / "clan_attrs.json"
    with locked_open(file, "w") as cfile:
        json.dump(clan_attrset, cfile, indent=2)

    commit_file(file, flake.path, "Add clan attributes")


# Common function to test clan nix attrset
def nix_attr_tester(
    test_flake_with_core: FlakeForTest,
    injected: dict[str, Any],
    expected_self: dict[str, Any],
    test_number: int,
) -> ClanExports:
    write_clan_attr(injected, test_flake_with_core)
    clan_dir = Flake(str(test_flake_with_core.path))
    nix_attrset = get_clan_nix_attrset(clan_dir)

    def recursive_sort(item: Any) -> Any:
        if isinstance(item, dict):
            return {k: recursive_sort(item[k]) for k in sorted(item)}
        if isinstance(item, list):
            return sorted(recursive_sort(elem) for elem in item)
        return item

    returned_sorted = recursive_sort(nix_attrset["self"])
    expected_sorted = recursive_sort(expected_self["self"])

    assert json.dumps(returned_sorted, indent=2) == json.dumps(
        expected_sorted, indent=2
    )
    return nix_attrset


@pytest.mark.impure
def test_copy_from_nixstore_symlink(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> None:
    src = temporary_home / "src"
    src.mkdir()
    (src / "file.txt").write_text("magicstring!")
    res = run(nix_command(["store", "add", str(src)]))
    src_nix = Path(res.stdout.strip())
    src2 = temporary_home / "src2"
    src2.mkdir()
    (src2 / "file.txt").symlink_to(src_nix / "file.txt")
    res = run(nix_command(["store", "add", str(src2)]))
    src2_nix = Path(res.stdout.strip())
    dest = temporary_home / "dest"
    copy_from_nixstore(src2_nix, dest)
    assert (dest / "file.txt").exists()
    assert (dest / "file.txt").read_text() == "magicstring!"
    assert (dest / "file.txt").is_symlink()


@pytest.mark.impure
def test_clan_core_templates(
    test_flake_with_core: FlakeForTest,
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
) -> None:
    clan_dir = Flake(str(test_flake_with_core.path))
    nix_attrset = get_clan_nix_attrset(clan_dir)

    clan_core_templates = nix_attrset["inputs"][InputName("clan-core")]["templates"][
        "clan"
    ]
    clan_core_template_keys = list(clan_core_templates.keys())

    expected_templates = ["default", "flake-parts", "minimal", "minimal-flake-parts"]
    assert clan_core_template_keys == expected_templates

    vlist_temps = list_templates("clan", clan_dir)
    list_template_keys = list(vlist_temps.inputs[InputName("clan-core")].keys())
    assert list_template_keys == expected_templates

    default_template = get_template(
        TemplateName("default"),
        "clan",
        input_prio=None,
        clan_dir=clan_dir,
    )

    new_clan = temporary_home / "new_clan"
    copy_from_nixstore(
        Path(default_template.src["path"]),
        new_clan,
    )
    assert (new_clan / "flake.nix").exists()
    assert (new_clan / "machines").is_dir()
    assert (new_clan / "machines" / "jon").is_dir()
    config_nix_p = new_clan / "machines" / "jon" / "configuration.nix"
    assert (config_nix_p).is_file()

    # Test if we can write to the configuration.nix file
    with config_nix_p.open("r+") as f:
        data = f.read()
        f.write(data)


# Test Case 1: Minimal input with empty templates
@pytest.mark.with_core
def test_clan_get_nix_attrset_case_1(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    test_flake_with_core: FlakeForTest,
) -> None:
    test_number = 1
    injected = {"templates": {"disko": {}, "machine": {}}}
    expected = {
        "inputs": {},
        "self": {"templates": {"disko": {}, "machine": {}, "clan": {}}},
    }
    nix_attr_tester(test_flake_with_core, injected, expected, test_number)


# Test Case 2: Input with one template under 'clan'
@pytest.mark.with_core
def test_clan_get_nix_attrset_case_2(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    test_flake_with_core: FlakeForTest,
) -> None:
    test_number = 2
    injected = {
        "templates": {
            "clan": {
                "example_template": {
                    "description": "An example clan template.",
                    "path": "/example/path",
                }
            }
        }
    }
    expected = {
        "inputs": {},
        "self": {
            "templates": {
                "clan": {
                    "example_template": {
                        "description": "An example clan template.",
                        "path": "/example/path",
                    }
                },
                "disko": {},
                "machine": {},
            },
        },
    }

    nix_attrset = nix_attr_tester(test_flake_with_core, injected, expected, test_number)

    assert "default" in list(
        nix_attrset["inputs"][InputName("clan-core")]["templates"]["clan"].keys()
    )


# Test Case 3: Input with templates under multiple types
@pytest.mark.with_core
def test_clan_get_nix_attrset_case_3(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    test_flake_with_core: FlakeForTest,
) -> None:
    test_number = 3
    injected = {
        "templates": {
            "clan": {
                "clan_template": {
                    "description": "A clan template.",
                    "path": "/clan/path",
                }
            },
            "disko": {
                "disko_template": {
                    "description": "A disko template.",
                    "path": "/disko/path",
                }
            },
            "machine": {
                "machine_template": {
                    "description": "A machine template.",
                    "path": "/machine/path",
                }
            },
        }
    }
    expected = {
        "inputs": {},
        "self": {
            "templates": {
                "clan": {
                    "clan_template": {
                        "description": "A clan template.",
                        "path": "/clan/path",
                    }
                },
                "disko": {
                    "disko_template": {
                        "description": "A disko template.",
                        "path": "/disko/path",
                    }
                },
                "machine": {
                    "machine_template": {
                        "description": "A machine template.",
                        "path": "/machine/path",
                    }
                },
            },
        },
    }
    nix_attr_tester(test_flake_with_core, injected, expected, test_number)


# Test Case 6: Input with missing 'templates' and 'modules' (empty clan attrset)
@pytest.mark.with_core
def test_clan_get_nix_attrset_case_6(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    test_flake_with_core: FlakeForTest,
) -> None:
    test_number = 6
    injected = {}
    expected = {
        "inputs": {},
        "self": {"templates": {"disko": {}, "machine": {}, "clan": {}}},
    }
    nix_attr_tester(test_flake_with_core, injected, expected, test_number)
