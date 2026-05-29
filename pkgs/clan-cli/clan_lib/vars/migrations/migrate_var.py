"""Shared utilities for vars file migrations.

Vars files may have sibling symlinks (sops encryption metadata: users/, groups/,
machines/ directories containing relative symlinks to clan_dir/sops/...).
When a vars file moves, its symlinks move with it
"""

import contextlib
import itertools
import logging
import os
import shutil
from pathlib import Path

log = logging.getLogger(__name__)


def _collect_symlinks(root: Path) -> dict[Path, Path]:
    symlinks = {}
    for dir_, dirnames, filenames in os.walk(root):
        dirpath = Path(dir_)
        for name in itertools.chain(dirnames, filenames):
            p = dirpath / name
            if p.is_symlink():
                rel = p.relative_to(root)
                symlinks[rel] = (p.parent / p.readlink()).resolve()
    return symlinks


def _relink_symlinks(src: Path, dst: Path, symlinks: dict[Path, Path]) -> None:
    for rel, resolved in symlinks.items():
        new_link = dst / rel
        res = resolved
        with contextlib.suppress(ValueError):
            res = dst / resolved.relative_to(src)
        new_target = os.path.relpath(res, new_link.parent)
        if new_link.readlink() == Path(new_target):
            continue
        new_link.unlink()
        new_link.symlink_to(new_target)


def _movetree_preserving_symlinks(src: Path, dst: Path) -> None:
    src, dst = Path(src).resolve(), Path(dst).resolve()
    symlinks = _collect_symlinks(src)
    shutil.move(str(src), str(dst))
    _relink_symlinks(src, dst, symlinks)


def _copytree_preserving_symlinks(src: Path, dst: Path) -> None:
    src, dst = Path(src).resolve(), Path(dst).resolve()
    symlinks = _collect_symlinks(src)
    shutil.copytree(src, dst, symlinks=True)
    _relink_symlinks(src, dst, symlinks)


def _collect_files(src: Path) -> list[Path]:
    result = []
    for p in src.iterdir():
        if p.is_dir() and not p.is_symlink():
            result.extend(_collect_files(p))
        else:
            result.append(p)
    return result


def delete_var_file(src: Path, changed: list[Path]) -> None:
    if not src.exists():
        return

    changed.extend(_collect_files(src))
    shutil.rmtree(src)


def copy_var_file(src: Path, dst: Path, changed: list[Path]) -> None:
    if not src.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    _copytree_preserving_symlinks(src, dst)
    changed.extend(_collect_files(dst))


def move_var_file(src: Path, dst: Path, changed: list[Path]) -> None:
    if not src.exists():
        return

    changed.extend(_collect_files(src))
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        changed.extend(_collect_files(dst))
        shutil.rmtree(dst)
    _movetree_preserving_symlinks(src, dst)
    changed.extend(_collect_files(dst))
