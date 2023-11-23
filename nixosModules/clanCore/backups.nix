{ lib, ... }:
{
  options.clanCore.state = lib.mkOption {
    default = { };
    type = lib.types.attrsOf
      (lib.types.submodule ({ name, ... }: {
        options = {
          folder = lib.mkOption {
            type = lib.types.str;
            default = name;
            description = ''
              Folder where state resides in
            '';
          };
        };
      }));
  };
  options.clanCore.backups = {
    providers = lib.mkOption {
      type = lib.types.attrsOf (lib.types.submodule ({ name, ... }: {
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
          delete = lib.mkOption {
            type = lib.types.str;
            description = ''
              script to delete a backup
            '';
          };
          start = lib.mkOption {
            type = lib.types.str;
            description = ''
              script to start a backup
            '';
          };
        };
      }));
      default = [ ];
      description = ''
        Configured backup providers which are used by this machine
      '';
    };
  };
}
