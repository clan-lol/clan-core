from clan_cli.machines.machines import Machine

from clan_lib.errors import ClanError


def create_backup(machine: Machine, provider: str | None = None) -> None:
    machine.info(f"creating backup for {machine.name}")
    backup_scripts = machine.eval_nix("config.clan.core.backups")
    if provider is None:
        if not backup_scripts["providers"]:
            msg = "No providers specified"
            raise ClanError(msg)
        with machine.target_host() as host:
            for provider in backup_scripts["providers"]:
                proc = host.run(
                    [backup_scripts["providers"][provider]["create"]],
                )
                if proc.returncode != 0:
                    msg = "failed to start backup"
                    raise ClanError(msg)
                print("successfully started backup")
    else:
        if provider not in backup_scripts["providers"]:
            msg = f"provider {provider} not found"
            raise ClanError(msg)
        with machine.target_host() as host:
            proc = host.run(
                [backup_scripts["providers"][provider]["create"]],
            )
        if proc.returncode != 0:
            msg = "failed to start backup"
            raise ClanError(msg)
        print("successfully started backup")
