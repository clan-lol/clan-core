from pathlib import Path

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_lib.flake import Flake
from clan_lib.templates import list_templates
from clan_lib.templates.filesystem import copy_from_nixstore


@pytest.mark.with_core
def test_clan_core_templates(
    test_flake_with_core: FlakeForTest,
    temporary_home: Path,
) -> None:
    clan_dir = Flake(str(test_flake_with_core.path))

    templates = list_templates(clan_dir)

    assert list(templates.builtins.get("clan", {}).keys()) == [
        "default",
        "flake-parts",
        "flake-parts-minimal",
        "minimal",
    ]

    # clan.default
    default_template = templates.builtins.get("clan", {}).get("default")
    assert default_template is not None

    template_path = default_template.get("path", None)
    assert template_path is not None

    my_clan = temporary_home / "my_clan"

    copy_from_nixstore(
        Path(template_path),
        my_clan,
    )

    flake_nix = my_clan / "flake.nix"
    assert (flake_nix).exists()
    assert (flake_nix).is_file()

    # Test if we can write to the flake.nix file
    with flake_nix.open("r+") as f:
        data = f.read()
        f.write(data)
