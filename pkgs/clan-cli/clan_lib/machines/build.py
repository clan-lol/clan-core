import logging
from dataclasses import dataclass

from clan_lib.async_run import is_async_cancelled
from clan_lib.cmd import run
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_build

log = logging.getLogger(__name__)


@dataclass
class BuildResult:
    """Result of building a machine configuration."""

    machine_name: str
    success: bool
    build_path: str | None = None
    symlink_path: str | None = None
    error_message: str | None = None


@dataclass
class BuildOptions:
    """Options for building machines."""

    format: str = "toplevel"
    dry_run: bool = False
    no_link: bool = False


def get_build_target(machine: Machine, build_format: str) -> str:
    """Get the nix build target for a machine.

    Special cases:
    - toplevel: config.system.build.toplevel
    - vm: config.system.build.vm
    - other formats: config.system.build.images.{format}
    """
    flake_ref = (
        machine.flake.identifier
        if not machine.flake.is_local
        else str(machine.flake.path)
    )

    if build_format == "toplevel":
        return f"{flake_ref}#nixosConfigurations.{machine.name}.config.system.build.toplevel"
    if build_format == "vm":
        return f"{flake_ref}#nixosConfigurations.{machine.name}.config.system.build.vm"

    # For all other formats, use config.system.build.images.{format}
    return f"{flake_ref}#nixosConfigurations.{machine.name}.config.system.build.images.{build_format}"


def build_machine(
    machine: Machine,
    options: BuildOptions | None = None,
) -> BuildResult:
    """Build a single machine configuration.

    Args:
        machine: The Machine instance to build.
        options: Build options (format, dry_run, no_link, etc.).

    Returns:
        BuildResult containing build information.

    Raises:
        ClanError: If the build fails or machine is invalid.

    """
    if options is None:
        options = BuildOptions()

    try:
        build_target = get_build_target(machine, options.format)
        nix_options = machine.flake.nix_options if machine.flake.nix_options else []

        build_flags = [build_target, *nix_options]
        if options.dry_run:
            build_flags.append("--dry-run")

        symlink_path = None
        if options.no_link:
            build_flags.append("--no-link")
        else:
            symlink_path = f"result-{machine.name}-{options.format}"
            build_flags.extend(["--out-link", symlink_path])

        cmd = nix_build(build_flags)

        proc = run(cmd)

        if is_async_cancelled():
            return BuildResult(
                machine_name=machine.name,
                success=False,
                error_message="Build cancelled by user",
            )

        build_path = proc.stdout.strip() if proc.stdout else None

        return BuildResult(
            machine_name=machine.name,
            success=True,
            build_path=build_path,
            symlink_path=symlink_path,
        )

    except ClanError as e:
        return BuildResult(
            machine_name=machine.name,
            success=False,
            error_message=str(e),
        )
