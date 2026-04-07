import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_lib.async_run import is_async_cancelled
from clan_lib.cmd import run
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.nix import current_system, nix_build, nix_test_store
from clan_lib.sandbox_exec import sandbox_cmd, sandbox_works
from clan_lib.vars.generate import run_generators
from clan_lib.vars.generator import get_machine_generators

log = logging.getLogger(__name__)


@dataclass
class BuildResult:
    """Result of building a machine configuration."""

    machine_name: str
    build_path: Path | None = None
    symlink_path: str | None = None


@dataclass
class BuildOptions:
    """Options for building machines."""

    format: str = "toplevel"
    dry_run: bool = False
    no_link: bool = False
    no_secrets: bool = False
    use_sandbox: bool = True


def get_build_target(machine: Machine, build_format: str) -> str:
    """Get the nix build target for a machine.

    Special cases:
    - toplevel: config.system.build.toplevel
    - other formats: config.system.build.images.{format}
    """
    flake_ref = (
        machine.flake.identifier
        if not machine.flake.is_local
        else str(machine.flake.path)
    )
    system = current_system()

    if build_format == "toplevel":
        return f'{flake_ref}#clanInternals.machines."{system}"."{machine.name}".config.system.build.toplevel'

    # For all other formats, use config.system.build.images.{format}
    return f'{flake_ref}#clanInternals.machines."{system}"."{machine.name}".config.system.build.images.{build_format}'


def _is_image_format(build_format: str) -> bool:
    """Check if the build format is an image format that supports secret injection."""
    return build_format not in ("toplevel")


def _find_image_file(build_dir: Path, build_format: str) -> Path:
    """Find the actual image file within a build output directory.

    Image builds output a directory (e.g., /nix/store/...-x86_64-linux.iso/)
    containing the image file in a subdirectory named after the format
    (e.g., iso/nixos-26.05-x86_64-linux.iso).
    """
    format_dir = build_dir / build_format
    if not format_dir.is_dir():
        msg = f"Expected directory {format_dir} not found in build output"
        raise ClanError(msg)
    files = [f for f in format_dir.iterdir() if f.is_file()]
    if len(files) != 1:
        msg = f"Expected exactly one file in {format_dir}, found {len(files)}"
        raise ClanError(msg)
    return files[0]


def _inject_secrets_into_image(
    machine: Machine,
    build_format: str,
    source_image_path: Path,
    output_path: Path,
    *,
    use_sandbox: bool = True,
) -> bool:
    """Inject secrets into a built image using the format's addFilesScript.

    Returns True if secrets were injected, False if skipped (no secrets).
    """
    # Get upload directory (e.g., /var/lib/sops-nix)
    secrets_target_dir = machine.secret_vars_store.get_upload_directory(machine.name)

    with TemporaryDirectory(prefix="clan-build-secrets-") as tmpdir:
        base_dir = Path(tmpdir).resolve()
        upload_dir = base_dir / secrets_target_dir.lstrip("/")
        upload_dir.mkdir(parents=True)

        generators = get_machine_generators([machine.name], machine.flake)
        machine.secret_vars_store.populate_dir(
            generators,
            machine.name,
            upload_dir,
            phases=["activation", "users", "services"],
        )

        # Check if any secrets were actually produced
        if not any(upload_dir.iterdir()):
            return False

        # Get the addFilesScript path from the NixOS config
        script_path = machine.flake.select_machine(
            machine.name,
            f"config.clan.core.image.{build_format}.addFilesScript",
        )

        # Remove stale output from previous runs (xorriso refuses to
        # write to an existing non-empty file when indev != outdev)
        output = Path(output_path)
        if output.exists():
            output.unlink()

        # Write the image into the tmpdir so the sandbox only needs
        # write access to the temp directory, not the final destination.
        sandbox_output = base_dir / "output" / output.name
        sandbox_output.parent.mkdir(parents=True)

        # Execute the addFilesScript; clean up partial output on failure
        inject_cmd: list[str] = [
            f"{script_path}/bin/add-files",
            "--source",
            str(source_image_path),
            "--output",
            str(sandbox_output),
            "--extra-path",
            str(base_dir),
            "/",
        ]

        # We want to be able to download and manage random clans
        # without needing code execution on the deployment machine.
        # And with this feature a clan could define the shell script
        # for building an ISO. This is why we are using bubblewrap here to sandbox
        # that shellscript
        if use_sandbox:
            if not sandbox_works():
                msg = (
                    "Cannot safely execute image secret injection: Sandboxing is not available on this system\n"
                    "Re-run 'machines build' with '--no-sandbox' to disable sandboxing"
                )
                raise ClanError(msg)
            with sandbox_cmd(
                inject_cmd,
                ro_paths=[str(base_dir)],
                rw_paths=[str(sandbox_output.parent)],
            ) as sandboxed_cmd:
                run(sandboxed_cmd)
        else:
            run(inject_cmd)

        # Move the finished image to the final destination
        shutil.move(str(sandbox_output), output_path)

    return True


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

    run_generators(
        [machine],
        generators=None,
        full_closure=False,
        no_sandbox=not options.use_sandbox,
    )

    build_target = get_build_target(machine, options.format)
    nix_options = machine.flake.nix_options or []

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
        msg = "Build cancelled"
        raise ClanError(msg)

    build_path = Path(proc.stdout.strip()) if proc.stdout else None

    # When using a custom test store, nix prints logical store paths (/nix/store/...)
    # but the actual files are under the store root.
    if build_path and (store := nix_test_store()):
        build_path = store / str(build_path).lstrip("/")

    # Post-build secret injection for image formats
    if (
        build_path
        and _is_image_format(options.format)
        and not options.no_secrets
        and not options.dry_run
    ):
        # build_path is a directory; resolve the actual image file inside
        source_file = _find_image_file(build_path, options.format)
        # Output to a file next to the symlink, named after the source file
        output_file = Path.cwd() / source_file.name

        secrets_injected = _inject_secrets_into_image(
            machine=machine,
            build_format=options.format,
            source_image_path=source_file,
            output_path=output_file,
            use_sandbox=options.use_sandbox,
        )
        if secrets_injected:
            log.warning(
                "This image contains secret key material "
                "(age private key). Treat this image as a sensitive "
                "artifact. Do not store it on shared or public media "
                "without encryption. Securely erase after use."
            )
            build_path = output_file

    return BuildResult(
        machine_name=machine.name,
        build_path=build_path,
        symlink_path=symlink_path,
    )
