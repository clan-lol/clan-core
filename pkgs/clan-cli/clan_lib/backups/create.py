from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.nix import current_system
from clan_lib.nix_selectors import machine_backups


def create_backup(machine: Machine, provider: str | None = None) -> None:
    machine.info(f"creating backup for {machine.name}")
    backup_scripts = machine.flake.select(
        machine_backups(current_system(), machine.name)
    )
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
