from clan_cli.machines.machines import Machine

from clan_lib.cmd import Log, RunOpts
from clan_lib.errors import ClanError
from clan_lib.ssh.remote import Remote


def restore_service(
    machine: Machine, host: Remote, name: str, provider: str, service: str
) -> None:
    backup_metadata = machine.eval_nix("config.clan.core.backups")
    backup_folders = machine.eval_nix("config.clan.core.state")

    if service not in backup_folders:
        msg = f"Service {service} not found in configuration. Available services are: {', '.join(backup_folders.keys())}"
        raise ClanError(msg)

    folders = backup_folders[service]["folders"]
    env = {}
    env["NAME"] = name
    # FIXME: If we have too many folder this might overflow the stack.
    env["FOLDERS"] = ":".join(set(folders))

    with host.ssh_control_master() as ssh:
        if pre_restore := backup_folders[service]["preRestoreCommand"]:
            proc = ssh.run(
                [pre_restore],
                RunOpts(log=Log.STDERR),
                extra_env=env,
            )
            if proc.returncode != 0:
                msg = f"failed to run preRestoreCommand: {pre_restore}, error was: {proc.stdout}"
                raise ClanError(msg)

        proc = ssh.run(
            [backup_metadata["providers"][provider]["restore"]],
            RunOpts(log=Log.STDERR),
            extra_env=env,
        )
        if proc.returncode != 0:
            msg = f"failed to restore backup: {backup_metadata['providers'][provider]['restore']}"
            raise ClanError(msg)

        if post_restore := backup_folders[service]["postRestoreCommand"]:
            proc = ssh.run(
                [post_restore],
                RunOpts(log=Log.STDERR),
                extra_env=env,
            )
            if proc.returncode != 0:
                msg = f"failed to run postRestoreCommand: {post_restore}, error was: {proc.stdout}"
                raise ClanError(msg)


def restore_backup(
    machine: Machine,
    provider: str,
    name: str,
    service: str | None = None,
) -> None:
    errors = []
    host = machine.target_host()
    with host.ssh_control_master():
        if service is None:
            backup_folders = machine.eval_nix("config.clan.core.state")
            for _service in backup_folders:
                try:
                    restore_service(machine, host, name, provider, _service)
                except ClanError as e:
                    errors.append(f"{_service}: {e}")
        else:
            try:
                restore_service(machine, host, name, provider, service)
            except ClanError as e:
                errors.append(f"{service}: {e}")
    if errors:
        raise ClanError(
            "Restore failed for the following services:\n" + "\n".join(errors)
        )
