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
      folder = "/var/backup/postgresql/${db.name}";
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
          while [[ "$(systemctl is-active postgres)" == activating ]]; then
            sleep 1
          done
          systemctl is-active postgres
          pg_dump -C ${db.name} | \
            ${pkgs.zstd}/bin/zstd --rsyncable | \
            > ${inProgressFile}
          mv ${inProgressFile} ${curFile}
        )
      '';
      postRestoreCommand = ''
        if [[ -f ${prevFile} ]]; then
          zstd --decompress --stdout ${prevFile} | psql -d ${db.name}
        fi
      '';
    };

  createDatabase = db: ''
    CREATE DATABASE "${db.name}" ${
      lib.concatStringsSep " " (
        lib.mapAttrsToList (name: value: "${name} = ':${value}'") db.createOptions
      )
    }
  '';
  cfg = config.clan.postgresql;

  userClauses = lib.mapAttrsToList (
    _: user: ""
    ''$PSQL -tAc "SELECT 1 FROM pg_roles WHERE rolname='${user.name}'" | grep -q 1 || $PSQL -tAc 'CREATE USER "${user.name}"' ''
  ) cfg.users;
  databaseClauses = lib.mapAttrsToList (
    name: db:
    lib.optionalString (db.create) ''$PSQL -d postgres -c "SELECT 1 FROM pg_database WHERE datname = '${name}'" | grep -q 1 || $PSQL -d postgres -c ${lib.escapeShellArg (createDatabase db)} ${createDatabaseArgs db}''
  ) cfg.databases;
in
{
  options.clan.postgresl = {
    databases = lib.mkOption {
      default = { };
      type = lib.types.attrsOf (
        lib.types.submodule (
          { name, ... }:
          {
            options = {
              name = lib.mkOption {
                type = lib.types.str;
                default = name;
              };
              # set to false, in case the upstream module uses ensureDatabase option
              create = lib.mkOption {
                type = lib.types.bool;
                default = true;
              };
              createOptions = lib.mkOption {
                type = lib.types.lazyAttrsOf lib.types.str;
                default = { };
                example = {
                  TEMPLATE = "template0";
                  LC_COLLATE = "C";
                  LC_CTYPE = "C";
                  ENCODING = "UTF8";
                  OWNER = "foo";
                };
              };
            };
          }
        )
      );
    };
    users = lib.mkOption {
      default = { };
      type = lib.types.attrsOf (
        lib.types.submodule (
          { name, ... }:
          {
            options.name = lib.mkOption {
              type = lib.types.str;
              default = name;
            };
          }
        )
      );
    };
  };
  config = {
    services.postgresql.enable = true;
    # We are duplicating a bit the upstream module but allow to create databases with options
    systemd.services.postgresql.postStart = ''
      PSQL="psql --port=${builtins.toString config.services.postgresql.settings.port}"

      while ! $PSQL -d postgres -c "" 2> /dev/null; do
          if ! kill -0 "$MAINPID"; then exit 1; fi
          sleep 0.1
      done
      ${lib.concatStringsSep "\n" userClauses}
      ${lib.concatStringsSep "\n" databaseClauses}
    '';
    clanCore.state = lib.mapAttrs' (
      _: db: lib.nameValuePair "postgresql-${db.name}" (createDatatbaseState db)
    ) config.clan.postgresql.databases;
  };
}
