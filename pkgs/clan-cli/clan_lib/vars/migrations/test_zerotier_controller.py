"""Tests for zerotier controller migration."""

from pathlib import Path

from .zerotier_controller import migrate_zerotier_controller


def _make_symlink(path: Path, target: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(target)


def _make_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_migration_moves_controller_to_shared(tmp_path: Path) -> None:
    """Controller's zerotier dir moves from per-machine to shared/zerotier-controller."""
    clan_dir = tmp_path
    pm = clan_dir / "vars" / "per-machine"

    # Controller machine "bam" with network-id
    _make_file(pm / "bam" / "zerotier" / "zerotier-network-id" / "value", "abc123")
    _make_file(pm / "bam" / "zerotier" / "zerotier-ip" / "value", "fd00::1")
    _make_file(
        pm / "bam" / "zerotier" / "zerotier-identity-secret" / "secret", "encrypted"
    )
    _make_symlink(
        pm / "bam" / "zerotier" / "zerotier-identity-secret" / "machines" / "bam",
        "../../../../../../sops/machines/bam",
    )
    _make_symlink(
        pm / "bam" / "zerotier" / "zerotier-identity-secret" / "users" / "admin",
        "../../../../../../sops/users/admin",
    )

    # Peer machine "jon" without network-id (should be untouched)
    _make_file(pm / "jon" / "zerotier" / "zerotier-ip" / "value", "fd00::2")

    migrate_zerotier_controller(clan_dir)

    # Controller moved to shared
    shared = clan_dir / "vars" / "shared" / "zerotier-controller"
    assert shared.exists()
    assert (shared / "zerotier-network-id" / "value").read_text() == "abc123"
    assert (shared / "zerotier-ip" / "value").read_text() == "fd00::1"
    assert (shared / "zerotier-identity-secret" / "secret").read_text() == "encrypted"

    # Old location is gone
    assert not (pm / "bam" / "zerotier").exists()

    # Symlinks fixed: 6 -> 5 levels
    machines_link = shared / "zerotier-identity-secret" / "machines" / "bam"
    assert machines_link.is_symlink()
    assert str(machines_link.readlink()) == "../../../../../sops/machines/bam"

    users_link = shared / "zerotier-identity-secret" / "users" / "admin"
    assert users_link.is_symlink()
    assert str(users_link.readlink()) == "../../../../../sops/users/admin"

    # Peer untouched
    assert (pm / "jon" / "zerotier" / "zerotier-ip" / "value").read_text() == "fd00::2"


def test_migration_noop_if_already_migrated(tmp_path: Path) -> None:
    """If shared/zerotier-controller exists, do nothing."""
    clan_dir = tmp_path
    shared = clan_dir / "vars" / "shared" / "zerotier-controller"
    shared.mkdir(parents=True)
    _make_file(shared / "zerotier-network-id" / "value", "abc123")

    # Also have old data (shouldn't be touched)
    pm = clan_dir / "vars" / "per-machine"
    _make_file(pm / "bam" / "zerotier" / "zerotier-network-id" / "value", "abc123")

    migrate_zerotier_controller(clan_dir)

    # Old data still there (not deleted since we skipped)
    assert (pm / "bam" / "zerotier" / "zerotier-network-id" / "value").exists()


def test_migration_noop_if_no_vars(tmp_path: Path) -> None:
    """No vars directory at all — should not crash."""
    migrate_zerotier_controller(tmp_path)


def test_migration_skips_if_multiple_controllers(tmp_path: Path) -> None:
    """Multiple machines with zerotier-network-id — refuse to migrate."""
    clan_dir = tmp_path
    pm = clan_dir / "vars" / "per-machine"

    _make_file(pm / "bam" / "zerotier" / "zerotier-network-id" / "value", "abc123")
    _make_file(pm / "jon" / "zerotier" / "zerotier-network-id" / "value", "def456")

    migrate_zerotier_controller(clan_dir)

    # Neither moved — shared dir not created
    assert not (clan_dir / "vars" / "shared" / "zerotier-controller").exists()
    # Both still in place
    assert (pm / "bam" / "zerotier" / "zerotier-network-id" / "value").exists()
    assert (pm / "jon" / "zerotier" / "zerotier-network-id" / "value").exists()


def test_migration_noop_if_no_controller(tmp_path: Path) -> None:
    """Peers only, no controller — should not migrate anything."""
    clan_dir = tmp_path
    pm = clan_dir / "vars" / "per-machine"
    _make_file(pm / "jon" / "zerotier" / "zerotier-ip" / "value", "fd00::2")

    migrate_zerotier_controller(clan_dir)

    assert not (clan_dir / "vars" / "shared" / "zerotier-controller").exists()
    assert (pm / "jon" / "zerotier" / "zerotier-ip" / "value").exists()
