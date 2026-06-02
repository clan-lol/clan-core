"""Tests for zerotier vars migration."""

from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

import pytest

from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.git import commit_files

from .zerotier import migrate_zerotier


def _make_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _make_symlink(path: Path, target: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(target)


MACHINES = ["controller1", "controller2", "peer1", "peer2", "peer3", "peer4"]

LEGACY_FILES: list[tuple[str, Literal["public", "secret"]]] = [
    # controller1 (controller for zt-net1)
    ("per-machine/controller1/zerotier/zerotier-network-id", "public"),
    ("per-machine/controller1/zerotier/zerotier-identity-secret", "secret"),
    ("per-machine/controller1/zerotier/zerotier-ip", "secret"),
    # peer1
    ("per-machine/peer1/zerotier/zerotier-identity-secret", "secret"),
    ("per-machine/peer1/zerotier/zerotier-ip", "public"),
    # peer2
    ("per-machine/peer2/zerotier/zerotier-identity-secret", "secret"),
    ("per-machine/peer2/zerotier/zerotier-ip", "public"),
    # controller2 (controller for zt-net2)
    ("per-machine/controller2/zerotier/zerotier-network-id", "public"),
    ("per-machine/controller2/zerotier/zerotier-identity-secret", "secret"),
    ("per-machine/controller2/zerotier/zerotier-ip", "secret"),
    # peer3
    ("per-machine/peer3/zerotier/zerotier-identity-secret", "secret"),
    ("per-machine/peer3/zerotier/zerotier-ip", "public"),
    # peer4
    ("per-machine/peer4/zerotier/zerotier-identity-secret", "secret"),
    ("per-machine/peer4/zerotier/zerotier-ip", "public"),
]

# Symlink targets at per-machine depth (6 levels from users/ or machines/ to repo root)
LINK_DEPTH_PER_MACHINE = "../../../../../../"
# Symlink targets at shared depth (5 levels)
LINK_DEPTH_SHARED = "../../../../../"

TWO_NETWORK_INVENTORY: dict[str, Any] = {
    "inventory": {
        "meta": {"name": "zt-migration-test"},
        "machines": {
            "controller1": {},
            "controller2": {},
            "peer1": {},
            "peer2": {},
            "peer3": {},
            "peer4": {},
            "stray": {},  # not in any zerotier instance
        },
        "instances": {
            "zt-net1": {
                "module": {"name": "zerotier"},
                "roles": {
                    "controller": {"machines": {"controller1": {}}},
                    "peer": {
                        "machines": {
                            "controller1": {},
                            "peer1": {},
                            "peer2": {},
                        }
                    },
                },
            },
            "zt-net2": {
                "module": {"name": "zerotier"},
                "roles": {
                    "controller": {"machines": {"controller2": {}}},
                    "peer": {
                        "machines": {
                            "controller2": {},
                            "peer3": {},
                            "peer4": {},
                        }
                    },
                },
            },
        },
    },
}


def _seed_legacy_files(vars_dir: Path, machines: set[str] | None = None) -> list[Path]:
    """Create LEGACY var files on disk. Returns all paths for git tracking.

    If *machines* is given, only seed files for those machines.
    """
    paths: list[Path] = []
    for v_path, v_type in LEGACY_FILES:
        # v_path is "per-machine/{machine}/zerotier/..."
        machine_name = v_path.split("/")[1]
        if machines is not None and machine_name not in machines:
            continue
        if v_type == "public":
            p = vars_dir / v_path / "value"
            _make_file(p, "fd00::1")
            paths.append(p)
        else:
            p = vars_dir / v_path / "secret"
            _make_file(p, "key-data")
            paths.append(p)
            link_user = vars_dir / v_path / "users" / "admin"
            _make_symlink(link_user, f"{LINK_DEPTH_PER_MACHINE}sops/users/admin")
            paths.append(link_user)
            link_machine = vars_dir / v_path / "machines" / "jon"
            _make_symlink(link_machine, f"{LINK_DEPTH_PER_MACHINE}sops/machines/jon")
            paths.append(link_machine)
    return paths


def _assert_secret_var(var_dir: Path, link_prefix: str) -> None:
    """Assert a secret var directory has the expected content and symlinks."""
    assert (var_dir / "secret").read_text() == "key-data"
    assert (
        str((var_dir / "users" / "admin").readlink())
        == f"{link_prefix}sops/users/admin"
    )
    assert (
        str((var_dir / "machines" / "jon").readlink())
        == f"{link_prefix}sops/machines/jon"
    )


def _assert_public_var(var_dir: Path, value: str = "fd00::1") -> None:
    """Assert a public var directory has the expected value."""
    assert (var_dir / "value").read_text() == value


def _assert_final_state(vars_dir: Path) -> None:
    """Assert the full FINAL all-shared directory structure after migration."""
    # 1. Shared identity secrets for every machine (not just controllers)
    for machine in MACHINES:
        _assert_secret_var(
            vars_dir / f"shared/zerotier-identity-{machine}/identity-secret",
            LINK_DEPTH_SHARED,
        )

    # 2. Shared network IDs (public), one per instance
    for inst in ["zt-net1", "zt-net2"]:
        _assert_public_var(vars_dir / f"shared/zerotier-network-{inst}/network-id")

    # 3. Shared IPs, generator name carries machine + instance.
    # Controllers have secret IPs; peers have public IPs.
    for ctrl, inst in [("controller1", "zt-net1"), ("controller2", "zt-net2")]:
        _assert_secret_var(
            vars_dir / f"shared/zerotier-ip-{ctrl}-{inst}/ip",
            LINK_DEPTH_SHARED,
        )
    for peer, inst in [
        ("peer1", "zt-net1"),
        ("peer2", "zt-net1"),
        ("peer3", "zt-net2"),
        ("peer4", "zt-net2"),
    ]:
        _assert_public_var(vars_dir / f"shared/zerotier-ip-{peer}-{inst}/ip")

    # 4. No per-machine zerotier generator dirs remain
    for machine in MACHINES:
        assert not (vars_dir / f"per-machine/{machine}/zerotier").exists(), (
            f"Legacy zerotier dir for {machine} should have been removed"
        )
        assert not (vars_dir / f"per-machine/{machine}/zerotier-identity").exists()
        assert not any((vars_dir / f"per-machine/{machine}").glob("zerotier-ip-*")), (
            f"Per-machine zerotier-ip dir for {machine} should have been removed"
        )
    assert not (vars_dir / "shared/zerotier-controller").exists()


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
class TestMigrateZerotier:
    def test_legacy(self, clan_flake: Callable[..., Flake]) -> None:
        """LEGACY state is migrated to FINAL; stray machine zerotier dir is removed."""
        flake = clan_flake(TWO_NETWORK_INVENTORY)
        clan_dir = flake.path
        vars_dir = clan_dir / "vars"

        paths = _seed_legacy_files(vars_dir)

        # Seed a stray machine: has legacy zerotier/ dir but is not in any
        # zerotier instance. Migration should remove the stale directory.
        stray_zt = vars_dir / "per-machine/stray/zerotier"
        stray_id = stray_zt / "zerotier-identity-secret"
        p = stray_id / "secret"
        _make_file(p, "key-data")
        paths.append(p)
        lu = stray_id / "users" / "admin"
        _make_symlink(lu, f"{LINK_DEPTH_PER_MACHINE}sops/users/admin")
        paths.append(lu)
        lm = stray_id / "machines" / "jon"
        _make_symlink(lm, f"{LINK_DEPTH_PER_MACHINE}sops/machines/jon")
        paths.append(lm)

        commit_files(
            file_paths=paths,
            flake_dir=clan_dir,
            commit_message="seed legacy zerotier vars",
        )

        migrate_zerotier(clan_dir)
        _assert_final_state(vars_dir)

        assert not stray_zt.exists(), "Stale zerotier dir should have been removed"

    def test_canonical(self, clan_flake: Callable[..., Flake]) -> None:
        """CANONICAL state (shared/zerotier-controller + per-machine) is migrated to FINAL."""
        flake = clan_flake(TWO_NETWORK_INVENTORY)
        clan_dir = flake.path
        vars_dir = clan_dir / "vars"

        # Seed per-machine legacy files (same as LEGACY)
        all_paths = _seed_legacy_files(vars_dir)

        # Seed the CANONICAL-only shared directory.
        # In CANONICAL state, shared/zerotier-controller/ has vars that the
        # migration deletes before processing per-machine dirs.
        canonical_shared = vars_dir / "shared/zerotier-controller"
        for var_name in [
            "zerotier-identity-secret",
            "zerotier-network-id",
            "zerotier-ip",
        ]:
            p = canonical_shared / var_name / "secret"
            _make_file(p, "stale-canonical-data")
            all_paths.append(p)

        commit_files(
            file_paths=all_paths,
            flake_dir=clan_dir,
            commit_message="seed canonical zerotier vars",
        )

        migrate_zerotier(clan_dir)
        _assert_final_state(vars_dir)

    def test_idempotent(self, clan_flake: Callable[..., Flake]) -> None:
        """Running migration twice produces the same FINAL state (second run is a no-op)."""
        flake = clan_flake(TWO_NETWORK_INVENTORY)
        clan_dir = flake.path
        vars_dir = clan_dir / "vars"

        legacy_paths = _seed_legacy_files(vars_dir)
        commit_files(
            file_paths=legacy_paths,
            flake_dir=clan_dir,
            commit_message="seed legacy zerotier vars",
        )

        migrate_zerotier(clan_dir)
        _assert_final_state(vars_dir)

        # Second run — _needs_migration returns False, nothing changes.
        migrate_zerotier(clan_dir)
        _assert_final_state(vars_dir)

    def test_multi_network_error(self, clan_flake: Callable[..., Flake]) -> None:
        """A machine in two zerotier instances raises ClanError."""
        # peer1 appears in both zt-net1 and zt-net2
        inventory: dict[str, Any] = {
            "inventory": {
                "meta": {"name": "zt-multi-err"},
                "machines": {
                    "controller1": {},
                    "controller2": {},
                    "peer1": {},
                },
                "instances": {
                    "zt-net1": {
                        "module": {"name": "zerotier"},
                        "roles": {
                            "controller": {"machines": {"controller1": {}}},
                            "peer": {"machines": {"controller1": {}, "peer1": {}}},
                        },
                    },
                    "zt-net2": {
                        "module": {"name": "zerotier"},
                        "roles": {
                            "controller": {"machines": {"controller2": {}}},
                            "peer": {"machines": {"controller2": {}, "peer1": {}}},
                        },
                    },
                },
            },
        }

        flake = clan_flake(inventory)
        clan_dir = flake.path
        vars_dir = clan_dir / "vars"

        # Need at least one legacy dir to pass the _needs_migration guard
        p = vars_dir / "per-machine/peer1/zerotier/zerotier-identity-secret/secret"
        _make_file(p, "key-data")
        commit_files(
            file_paths=[p],
            flake_dir=clan_dir,
            commit_message="seed vars for multi-network test",
        )

        with pytest.raises(ClanError, match="Automatic zerotier vars migration failed"):
            migrate_zerotier(clan_dir)

    def test_mixed_state(self, clan_flake: Callable[..., Flake]) -> None:
        """Only some machines have legacy zerotier/ dirs; others have none."""
        flake = clan_flake(TWO_NETWORK_INVENTORY)
        clan_dir = flake.path
        vars_dir = clan_dir / "vars"

        zt_net1 = {"controller1", "peer1", "peer2"}
        paths = _seed_legacy_files(vars_dir, machines=zt_net1)

        # Also seed CANONICAL shared dir (stale artifact from a partial earlier attempt)
        canonical = vars_dir / "shared/zerotier-controller"
        for var_name in [
            "zerotier-identity-secret",
            "zerotier-network-id",
            "zerotier-ip",
        ]:
            p = canonical / var_name / "secret"
            _make_file(p, "stale")
            paths.append(p)

        commit_files(
            file_paths=paths,
            flake_dir=clan_dir,
            commit_message="seed mixed state",
        )

        migrate_zerotier(clan_dir)

        _assert_public_var(vars_dir / "shared/zerotier-network-zt-net1/network-id")
        for m in zt_net1:
            _assert_secret_var(
                vars_dir / f"shared/zerotier-identity-{m}/identity-secret",
                LINK_DEPTH_SHARED,
            )
            assert not (vars_dir / f"per-machine/{m}/zerotier").exists()
        _assert_secret_var(
            vars_dir / "shared/zerotier-ip-controller1-zt-net1/ip",
            LINK_DEPTH_SHARED,
        )
        _assert_public_var(vars_dir / "shared/zerotier-ip-peer1-zt-net1/ip")
        _assert_public_var(vars_dir / "shared/zerotier-ip-peer2-zt-net1/ip")

        # zt-net2 machines had no legacy files — nothing was created for them
        for m in ["controller2", "peer3", "peer4"]:
            assert not (vars_dir / f"per-machine/{m}").exists()
        assert not (vars_dir / "shared/zerotier-identity-controller2").exists()
        assert not (vars_dir / "shared/zerotier-network-zt-net2").exists()

        assert not canonical.exists()

    def test_canonical_shared_only(self, clan_flake: Callable[..., Flake]) -> None:
        """shared/zerotier-controller is cleaned up even when per-machine is already FINAL."""
        flake = clan_flake(TWO_NETWORK_INVENTORY)
        clan_dir = flake.path
        vars_dir = clan_dir / "vars"

        legacy_paths = _seed_legacy_files(vars_dir)
        commit_files(
            file_paths=legacy_paths,
            flake_dir=clan_dir,
            commit_message="seed legacy",
        )
        migrate_zerotier(clan_dir)
        _assert_final_state(vars_dir)

        # Now plant a stale shared/zerotier-controller (leftover from CANONICAL)
        canonical = vars_dir / "shared/zerotier-controller"
        p = canonical / "zerotier-identity-secret" / "secret"
        _make_file(p, "stale")
        commit_files(
            file_paths=[p],
            flake_dir=clan_dir,
            commit_message="add stale canonical dir",
        )

        migrate_zerotier(clan_dir)
        assert not canonical.exists()
        _assert_final_state(vars_dir)
