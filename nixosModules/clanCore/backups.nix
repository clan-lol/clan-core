{ lib, ... }:
{
  imports = [ ./state.nix ];
  options.clanCore.backups = {
    providers = lib.mkOption {
      type = lib.types.attrsOf (
        lib.types.submodule (
          { name, ... }:
          {
            options = {
              name = lib.mkOption {
                type = lib.types.str;
                default = name;
                description = ''
                  Name of the backup provider
                '';
              };
              list = lib.mkOption {
                type = lib.types.str;
                description = ''
                  script to list backups
                '';
              };
              restore = lib.mkOption {
                type = lib.types.str;
                description = ''
                  script to restore a backup
                  should take an optional service name as argument
                  gets ARCHIVE_ID, LOCATION, JOB and FOLDERS as environment variables
                  ARCHIVE_ID is the id of the backup
                  LOCATION is the remote identifier of the backup
                  JOB is the job name of the backup
                  FOLDERS is a colon separated list of folders to restore
                '';
              };
              create = lib.mkOption {
                type = lib.types.str;
                description = ''
                  script to start a backup
                '';
              };
            };
          }
        )
      );
      default = { };
      description = ''
        Configured backup providers which are used by this machine
      '';
    };
  };
}
