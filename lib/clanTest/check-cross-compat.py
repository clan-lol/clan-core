"""Check that a derivation and all transitive dependencies match the expected system."""

import re
import sys
from pathlib import Path


def parse_env_var(name: str, content: str) -> str | None:
    """Extract a named env var from a .drv file's content.

    Handles both plain ATerm and structuredAttrs (__json) formats.
    """
    m = re.search(rf'\("{name}","([^"]+)"\)', content)
    if not m:
        m = re.search(rf'\\"{name}\\":\\"([^\\]+)\\"', content)
    return m.group(1) if m else None


def parse_drv(drv_path: str) -> tuple[str, str, list[str]]:
    """Parse a .drv file and extract system, pname, and input derivation paths.

    Returns (system, pkg_name, list_of_input_drv_paths).
    """
    content = Path(drv_path).read_text()

    # Extract inputDrvs: list of ("/nix/store/...drv", [...]) pairs
    input_drv_paths = re.findall(r'\("/nix/store/[^"]+\.drv"', content)
    input_drvs = [p.strip('("') for p in input_drv_paths]

    system = parse_env_var("system", content)
    if not system:
        msg = f"could not parse system from {drv_path}"
        raise ValueError(msg)

    pkg_name = (
        parse_env_var("pname", content) or parse_env_var("name", content) or "package"
    )

    return system, pkg_name, input_drvs


def check_system(
    drv_path: str,
    expected_system: str,
    visited: set[str],
) -> list[tuple[str, str]]:
    """Recursively check that drv and its inputDrvs have the expected system.

    Returns a list of (drv_path, pkg_name) tuples for any mismatches.
    """
    if drv_path in visited:
        return []
    visited.add(drv_path)

    if not Path(drv_path).exists():
        return [(drv_path, "package")]

    system, pkg_name, input_drvs = parse_drv(drv_path)
    errors: list[tuple[str, str]] = []

    # "builtin" system is used by fixed-output fetchers (source downloads),
    # these are platform-independent and can be skipped.
    if system == "builtin":
        return []

    if system != expected_system:
        # Don't recurse into dependencies of a mismatched derivation:
        # they will typically have the same issue since the whole subtree
        # is pinned to the wrong platform.  We still continue searching
        # sibling branches (breadth) via the caller's loop.
        return [(drv_path, pkg_name)]

    for input_drv_path in input_drvs:
        errors.extend(check_system(input_drv_path, expected_system, visited))

    return errors


EXPECTED_ARGC = 4


def format_error(module_name: str, drv_path: str, pkg_name: str) -> str:
    """Format an error message for a derivation with a mismatched system."""
    return f"""\
Cross-platform compatibility check failed for NixOS module '{module_name}'.

The dependency derivation {drv_path} is pinned to a specific platform \
instead of being resolved through nixpkgs.

Using pkgs.callPackage is required to allow systems not explicitly \
supported by the maintainer to import the module, and to support \
cross compilation.

The most common cause for this error is referencing a package via a \
flake output, e.g.:

  my-flake.packages.${{system}}.{pkg_name}

Instead, use pkgs.callPackage so the package is built for the correct platform:

  pkgs.callPackage (my-flake + "/packages/{pkg_name}.nix") {{}}

(The actual file path may differ; this is just an example.)
"""


def main() -> None:
    if len(sys.argv) != EXPECTED_ARGC:
        print(
            f"Usage: {sys.argv[0]} <module-name> <drv-path> <expected-system>",
            file=sys.stderr,
        )
        sys.exit(1)

    module_name = sys.argv[1]
    drv_path = sys.argv[2]
    expected_system = sys.argv[3]

    errors = check_system(drv_path, expected_system, set())

    if errors:
        for err_drv_path, pkg_name in errors:
            print(format_error(module_name, err_drv_path, pkg_name), file=sys.stderr)
        sys.exit(1)

    print(
        f"All derivations in the closure of '{module_name}' have system '{expected_system}'"
    )


if __name__ == "__main__":
    main()
