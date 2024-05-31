{
  pkgs,
  lib,
  config,
  ...
}:
let
  createDatatbaseState =
    db:
    let
      folder = "/var/backup/postgresql/${db}";
      curFile = "${folder}/dump.sql.zstd";
      prevFile = "${folder}/dump.sql.prev.zstd";
      inProgressFile = "${folder}/dump.sql.in-progress.zstd";
    in
    {
      folders = [ folder ];
      preBackupCommand = ''
        (
          umask 0077 # ensure backup is only readable by postgres user
          if [ -e ${curFile} ]; then
            mv ${curFile} ${prevFile}
          fi
          pg_dump -C ${db} | \
            ${pkgs.zstd}/bin/zstd --rsyncable | \
            > ${inProgressFile}
          mv ${inProgressFile} ${curFile}
        )
      '';
      postRestoreCommand = ''
        if [[ -f ${prevFile} ]]; then
          zstd --decompress --stdout ${prevFile} | psql -d ${db}
        fi
      '';
    };
in
{
  options.clan.postgresl = {
    databases = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ "clan" ];
    };
  };
  config = {
    services.postgresql.enable = true;
    clanCore.state = lib.listToAttrs (
      builtins.map (
        db: lib.nameValuePair "postgresql-${db}" (createDatatbaseState db)
      ) config.clan.postgresl.databases
    );
  };
}
