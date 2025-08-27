import json

import pytest
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.templates.disk import set_machine_disk_schema

from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli


@pytest.mark.with_core
def test_templates_apply_machine_and_disk(
    test_flake_with_core: FlakeForTest,
) -> None:
    """Test both machine template creation and disk template application."""
    flake_path = str(test_flake_with_core.path)

    cli.run(
        [
            "templates",
            "apply",
            "machine",
            "new-machine",
            "test-apply-machine",
            "--flake",
            flake_path,
        ]
    )

    # Verify machine was created
    machine_dir = test_flake_with_core.path / "machines" / "test-apply-machine"
    assert machine_dir.exists(), "Machine directory should be created"
    assert (machine_dir / "configuration.nix").exists(), (
        "Configuration file should exist"
    )

    facter_content = {
        "disks": [
            {
                "name": "test-disk",
                "path": "/dev/sda",
                "size": 107374182400,
                "type": "disk",
            }
        ]
    }

    facter_path = machine_dir / "facter.json"
    facter_path.write_text(json.dumps(facter_content, indent=2))

    machine = Machine(name="test-apply-machine", flake=Flake(flake_path))
    set_machine_disk_schema(
        machine,
        "single-disk",
        {"mainDisk": "/dev/sda"},
        force=False,
        check_hw=False,  # Skip hardware validation for test
    )

    # Verify disk template was applied by checking that disko.nix exists or was updated
    disko_file = machine_dir / "disko.nix"
    assert disko_file.exists(), "Disko configuration should be created"

    # Verify error handling - try to create duplicate machine
    # Since apply machine now uses machines create, it raises ClanError for duplicates
    with pytest.raises(ClanError, match="already exists"):
        cli.run(
            [
                "templates",
                "apply",
                "machine",
                "new-machine",
                "test-apply-machine",  # Same name as existing
                "--flake",
                flake_path,
            ]
        )
