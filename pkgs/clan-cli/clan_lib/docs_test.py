import ast
from pathlib import Path

import pytest

from clan_lib.docs import (
    DOCS_BASE_URL,
    DOCS_VERSION,
    guides_url,
    reference_url,
)

# clan_lib/ -> pkgs/clan-cli/
_CLI_ROOT = Path(__file__).parent.parent

# Source directories whose `docs_url()` calls are validated against the docs.
_SOURCE_ROOTS = ("clan_cli", "clan_lib")


def _is_test_file(path: Path) -> bool:
    return path.name.startswith("test_") or path.name.endswith("_test.py")


def _called_function_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _collect_function_calls(function_name: str) -> list[tuple[Path, int, str]]:
    """Find every invocation of function_name in clan_cli and clan_lib"""
    calls: list[tuple[Path, int, str]] = []
    non_literal: list[str] = []
    for root in _SOURCE_ROOTS:
        for py_file in sorted((_CLI_ROOT / root).rglob("*.py")):
            if _is_test_file(py_file):
                continue
            tree = ast.parse(py_file.read_text(), filename=str(py_file))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if _called_function_name(node) != function_name or not node.args:
                    continue
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    calls.append((py_file, node.lineno, arg.value))
                else:
                    rel = py_file.relative_to(_CLI_ROOT)
                    non_literal.append(f"{rel}:{node.lineno}")
    if non_literal:
        joined = "\n  ".join(non_literal)
        pytest.fail(
            f"{function_name} must be called with a string literal so the target "
            f"page can be validated. Non-literal calls found:\n  {joined}"
        )
    return calls


def test_docs_url_builds_versioned_url() -> None:
    assert guides_url("guides/backups/intro-to-backups") == (
        f"{DOCS_BASE_URL}/{DOCS_VERSION}/guides/backups/intro-to-backups"
    )
    assert guides_url("/guides/specialisations/") == (
        f"{DOCS_BASE_URL}/{DOCS_VERSION}/guides/specialisations"
    )
    assert guides_url("") == f"{DOCS_BASE_URL}/{DOCS_VERSION}"


@pytest.mark.with_core
def test_guides_url_pages_exist(clan_core: Path) -> None:
    """Every `docs_url()` call in the CLI must reference an existing docs page."""
    docs_src = clan_core / "docs" / "src"
    assert docs_src.is_dir(), (
        f"Documentation source not found at {docs_src}. The clan-core checkout "
        "used for `with_core` tests must include docs/src."
    )

    calls = _collect_function_calls("guides_url")
    assert calls, "no guides_url() calls found - the AST collector is broken"

    missing: list[str] = []
    for py_file, lineno, page in calls:
        page_path = page.split("#", 1)[0].strip("/")
        if not page_path:
            # The empty path links to the documentation home page.
            continue
        if not (docs_src / f"{page_path}.md").is_file():
            rel = py_file.relative_to(_CLI_ROOT)
            missing.append(f"{rel}:{lineno} -> docs/src/{page_path}.md")

    assert not missing, "guides_url() points at missing documentation pages:\n  " + (
        "\n  ".join(missing)
    )


def test_reference_url() -> None:
    assert reference_url("cli") == f"{DOCS_BASE_URL}/{DOCS_VERSION}/reference/cli"
