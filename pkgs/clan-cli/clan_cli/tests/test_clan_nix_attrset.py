from pathlib import Path

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_lib.cmd import run
from clan_lib.flake import Flake
from clan_lib.nix import nix_command
from clan_lib.templates import list_templates
from clan_lib.templates.filesystem import copy_from_nixstore


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
