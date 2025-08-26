from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine


def create_backup(machine: Machine, provider: str | None = None) -> None:
    machine.info(f"creating backup for {machine.name}")
    backup_scripts = machine.select("config.clan.core.backups")
    host = machine.target_host()
    if provider is None:
        if not backup_scripts["providers"]:
            msg = "No providers specified"
            raise ClanError(msg)
        with host.host_connection() as ssh:
            for prov in backup_scripts["providers"]:
                proc = ssh.run(
                    [backup_scripts["providers"][prov]["create"]],
                )
                if proc.returncode != 0:
                    msg = "failed to start backup"
                    raise ClanError(msg)
                print("successfully started backup")
    else:
        if provider not in backup_scripts["providers"]:
            msg = f"provider {provider} not found"
            raise ClanError(msg)
        with host.host_connection() as ssh:
            proc = ssh.run(
                [backup_scripts["providers"][provider]["create"]],
            )
        if proc.returncode != 0:
            msg = "failed to start backup"
            raise ClanError(msg)
        print("successfully started backup")
