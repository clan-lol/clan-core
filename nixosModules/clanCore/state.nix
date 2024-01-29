{ lib, ... }:
{
  # defaults
  # FIXME: currently broken, will be fixed soon
  #config.clanCore.state.HOME.folders = [ "/home" ];

  # interface
  options.clanCore.state = lib.mkOption {
    default = { };
    type = lib.types.attrsOf
      (lib.types.submodule ({ ... }: {
        options = {
          folders = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            description = ''
              Folder where state resides in
            '';
          };
          preRestoreScript = lib.mkOption {
            type = lib.types.str;
            default = ":";
            description = ''
              script to run before restoring the state dir from a backup

              Utilize this to stop services which currently access these folders
            '';
          };
          postRestoreScript = lib.mkOption {
            type = lib.types.str;
            default = ":";
            description = ''
              script to restore the service after the state dir was restored from a backup

              Utilize this to start services which were previously stopped
            '';
          };
        };
      }));
  };
}
