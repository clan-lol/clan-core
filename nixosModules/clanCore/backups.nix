{ lib, ... }:
{
  imports = [ ./state.nix ];
  options.clan.core.backups = {
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
                  Command to list backups.
                '';
              };
              restore = lib.mkOption {
                type = lib.types.str;
                description = ''
                  Command to restore a backup.
                  The name of the backup and the folders to restore will be
                  set as environment variables NAME and FOLDERS respectively.
                '';
              };
              create = lib.mkOption {
                type = lib.types.str;
                description = ''
                  Command to start a backup
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
