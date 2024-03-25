{
  lib,
  config,
  pkgs,
  ...
}:
{
  services.postgresql.enable = true;
  services.postgresqlBackup = {
    enable = lib.mkDefault true;
    startAt = lib.mkDefault [ ]; # we will start this as part of the backup
    compression = "zstd";
  };
  clanCore.state.postgres.folders = [ "/var/backup/postgresql" ];

  assertions = [
    ({
      assertion = config.postgresqlBackup.databases == [ ];
      message = "We currently do not support backing up specific databases. Please set postgresqlBackup.databases to an empty list. Or disable services.postgresqlBackup.enable";
    })
  ];

  clanCore.state.postgres.postRestoreScript = ''
    for dump in /var/backup/postgresql/all*; do
      case "$dump" in
        *.gz) decompressionCmd="${pkgs.gzip}/bin/gzip -d -${toString config.services.postgresqlBackup.compressionLevel}" ;;
        *.zst) decompressionCmd="${pkgs.zstd}/bin/zstd -d -${toString config.services.postgresqlBackup.compressionLevel}" ;;
        *) decompressionCmd="cat" ;;
      esac
      $decompressionCmd $dump | psql template1
      break
    done
  '';

  services.borgbackup.jobs.${config.networking.hostName} = {
    preHook = ''
      ${pkgs.systemd}/bin/systemctl start postgresqlBackup
    '';
  };
}
