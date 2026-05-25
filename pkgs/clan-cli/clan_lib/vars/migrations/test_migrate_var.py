"""Tests for vars migration utilities."""

from pathlib import Path

from .migrate_var import copy_var_file, delete_var_file, move_var_file


def _make_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _make_symlink(path: Path, target: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(target)


class TestMoveVarFile:
    def test_basic(self, tmp_path: Path) -> None:
        """Move a leaf directory with a file and a symlink."""
        vars_dir = tmp_path / "vars"
        src = vars_dir / "per-machine" / "bam" / "zerotier" / "zerotier-ip"
        dst = vars_dir / "per-machine" / "bam" / "zerotier-net" / "ip"

        _make_file(src / "value", "fd00::1")

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        assert not src.exists()
        assert (dst / "value").read_text() == "fd00::1"
        assert len(changed) == 2  # old + new

    def test_fixes_symlinks(self, tmp_path: Path) -> None:
        """Symlinks are rewritten after move."""
        vars_dir = tmp_path / "vars"
        src = vars_dir / "per-machine" / "bam" / "zerotier" / "identity-secret"
        dst = vars_dir / "per-machine" / "bam" / "zerotier-identity" / "identity-secret"

        _make_file(src / "secret", "key-data")
        _make_symlink(src / "users" / "admin", "../../../../../../sops/users/admin")
        _make_symlink(src / "machines" / "bam", "../../../../../../sops/machines/bam")

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        # Same depth, symlinks should be unchanged
        assert (
            str((dst / "users" / "admin").readlink())
            == "../../../../../../sops/users/admin"
        )

        # Verify file moved
        assert (dst / "secret").read_text() == "key-data"
        assert not src.exists()

    def test_decreases_symlink_depth(self, tmp_path: Path) -> None:
        """Moving from per-machine (deeper) to shared (shallower) adjusts symlinks."""
        vars_dir = tmp_path / "vars"
        # per-machine/bam/zerotier/network-id -> depth 6 for users/admin symlink
        src = vars_dir / "per-machine" / "bam" / "zerotier" / "zerotier-network-id"
        # shared/zerotier-network-net/network-id -> depth 5 for users/admin symlink
        dst = vars_dir / "shared" / "zerotier-network-net" / "network-id"

        _make_file(src / "value", "abc123")
        _make_symlink(src / "users" / "admin", "../../../../../../sops/users/admin")

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        # Depth went from 6 to 5, one fewer ../
        assert (
            str((dst / "users" / "admin").readlink())
            == "../../../../../sops/users/admin"
        )

    def test_increases_symlink_depth(self, tmp_path: Path) -> None:
        """Moving from shared (shallower) to per-machine (deeper) adds ../ levels."""
        vars_dir = tmp_path / "vars"
        src = vars_dir / "shared" / "zerotier-net" / "network-id"
        dst = vars_dir / "per-machine" / "bam" / "zerotier" / "zerotier-network-id"

        _make_file(src / "value", "abc123")
        _make_symlink(src / "users" / "admin", "../../../../../sops/users/admin")

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        # Depth went from 5 to 6, one more ../
        assert (
            str((dst / "users" / "admin").readlink())
            == "../../../../../../sops/users/admin"
        )

    def test_internal_symlink(self, tmp_path: Path) -> None:
        """Symlink pointing inside the moved tree is remapped to new location."""
        vars_dir = tmp_path / "vars"
        src = vars_dir / "per-machine" / "bam" / "svc" / "my-var"

        _make_file(src / "value", "hello")
        # Symlink that resolves inside src (pointing at sibling file)
        _make_symlink(src / "link", "value")

        changed: list[Path] = []
        dst = vars_dir / "shared" / "svc" / "my-var"
        move_var_file(src, dst, changed)

        # The symlink still points at "value" inside the new location
        link = dst / "link"
        assert link.is_symlink()
        assert link.resolve() == (dst / "value").resolve()
        assert (dst / "value").read_text() == "hello"

    def test_nested_subdirectories(self, tmp_path: Path) -> None:
        """Move a tree with multiple nested files and symlinks at different depths."""
        vars_dir = tmp_path / "vars"
        src = vars_dir / "per-machine" / "bam" / "svc" / "my-var"
        dst = vars_dir / "per-machine" / "bam" / "svc-v2" / "my-var"

        _make_file(src / "secret", "s")
        _make_file(src / "sub" / "nested", "n")
        _make_symlink(src / "users" / "admin", "../../../../../../sops/users/admin")
        _make_symlink(src / "machines" / "bam", "../../../../../../sops/machines/bam")

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        assert not src.exists()
        assert (dst / "secret").read_text() == "s"
        assert (dst / "sub" / "nested").read_text() == "n"
        assert (dst / "users" / "admin").is_symlink()
        assert (dst / "machines" / "bam").is_symlink()
        # 4 items at src + 4 at dst
        assert len(changed) == 8

    def test_creates_dst_parents(self, tmp_path: Path) -> None:
        """Intermediate directories for dst are created automatically."""
        src = tmp_path / "a"
        dst = tmp_path / "deeply" / "nested" / "path" / "b"

        _make_file(src / "value", "data")

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        assert (dst / "value").read_text() == "data"
        assert not src.exists()

    def test_changed_contains_all_leaves(self, tmp_path: Path) -> None:
        """Changed list includes every file and symlink, from both src and dst."""
        src = tmp_path / "src"
        dst = tmp_path / "dst"

        _make_file(src / "a", "1")
        _make_file(src / "b", "2")
        _make_symlink(src / "c", "a")

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        # 3 from src (pre-move snapshot) + 3 from dst
        assert len(changed) == 6
        # dst entries are present
        dst_entries = {p for p in changed if dst in p.parents or p == dst}
        assert len(dst_entries) == 3

    def test_noop_if_missing(self, tmp_path: Path) -> None:
        """No error if src doesn't exist."""
        vars_dir = tmp_path / "vars"
        src = vars_dir / "nonexistent"
        dst = vars_dir / "target"

        changed: list[Path] = []
        move_var_file(src, dst, changed)

        assert changed == []
        assert not dst.exists()


class TestCopyVarFile:
    def test_basic(self, tmp_path: Path) -> None:
        """Copy a directory with a plain file."""
        src = tmp_path / "src"
        dst = tmp_path / "dst"

        _make_file(src / "value", "hello")

        changed: list[Path] = []
        copy_var_file(src, dst, changed)

        # Source survives
        assert (src / "value").read_text() == "hello"
        # Destination created
        assert (dst / "value").read_text() == "hello"
        assert len(changed) == 1

    def test_fixes_symlinks(self, tmp_path: Path) -> None:
        """Symlinks in the copy are rewritten to point from the new location."""
        vars_dir = tmp_path / "vars"
        src = vars_dir / "per-machine" / "bam" / "svc" / "my-var"
        dst = vars_dir / "shared" / "svc" / "my-var"

        _make_file(src / "secret", "data")
        _make_symlink(src / "users" / "admin", "../../../../../../sops/users/admin")

        changed: list[Path] = []
        copy_var_file(src, dst, changed)

        # Source unchanged
        assert (
            str((src / "users" / "admin").readlink())
            == "../../../../../../sops/users/admin"
        )
        # Dest symlink adjusted (one level shallower)
        assert (
            str((dst / "users" / "admin").readlink())
            == "../../../../../sops/users/admin"
        )

    def test_internal_symlink(self, tmp_path: Path) -> None:
        """Symlink pointing within the tree is correct in the copy."""
        src = tmp_path / "src"
        dst = tmp_path / "dst"

        _make_file(src / "value", "data")
        _make_symlink(src / "alias", "value")

        changed: list[Path] = []
        copy_var_file(src, dst, changed)

        alias = dst / "alias"
        assert alias.is_symlink()
        assert alias.resolve() == (dst / "value").resolve()

    def test_creates_dst_parents(self, tmp_path: Path) -> None:
        """Intermediate directories for dst are created."""
        src = tmp_path / "src"
        dst = tmp_path / "a" / "b" / "c" / "dst"

        _make_file(src / "value", "x")

        changed: list[Path] = []
        copy_var_file(src, dst, changed)

        assert (dst / "value").read_text() == "x"
        assert (src / "value").read_text() == "x"

    def test_noop_if_missing(self, tmp_path: Path) -> None:
        """No error if src doesn't exist."""
        src = tmp_path / "nonexistent"
        dst = tmp_path / "target"

        changed: list[Path] = []
        copy_var_file(src, dst, changed)

        assert changed == []
        assert not dst.exists()


class TestDeleteVarFile:
    def test_basic(self, tmp_path: Path) -> None:
        """Delete a directory with files."""
        src = tmp_path / "src"
        _make_file(src / "value", "gone")
        _make_file(src / "secret", "also gone")

        changed: list[Path] = []
        delete_var_file(src, changed)

        assert not src.exists()
        assert len(changed) == 2

    def test_with_symlinks(self, tmp_path: Path) -> None:
        """Delete a directory containing symlinks -- changed includes them."""
        src = tmp_path / "src"
        _make_file(src / "secret", "data")
        _make_symlink(src / "users" / "admin", "../../../sops/users/admin")
        _make_symlink(src / "machines" / "bam", "../../../sops/machines/bam")

        changed: list[Path] = []
        delete_var_file(src, changed)

        assert not src.exists()
        # 1 file + 2 symlinks
        assert len(changed) == 3

    def test_nested(self, tmp_path: Path) -> None:
        """Delete a deeply nested tree -- all leaves reported."""
        src = tmp_path / "src"
        _make_file(src / "a", "1")
        _make_file(src / "sub" / "b", "2")
        _make_file(src / "sub" / "deep" / "c", "3")

        changed: list[Path] = []
        delete_var_file(src, changed)

        assert not src.exists()
        assert len(changed) == 3

    def test_noop_if_missing(self, tmp_path: Path) -> None:
        """No error if src doesn't exist."""
        src = tmp_path / "nonexistent"

        changed: list[Path] = []
        delete_var_file(src, changed)

        assert changed == []
