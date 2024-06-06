{ lib, ... }:
{
  # defaults
  config.clanCore.state.HOME.folders = [ "/home" ];

  # interface
  options.clanCore.state = lib.mkOption {
    default = { };
    type = lib.types.attrsOf (
      lib.types.submodule (
        { name, ... }:
        {
          options = {
            name = lib.mkOption {
              type = lib.types.str;
              default = name;
              description = ''
                Name of the state
              '';
            };
            folders = lib.mkOption {
              type = lib.types.listOf lib.types.str;
              description = ''
                Folder where state resides in
              '';
            };
            preBackupCommand = lib.mkOption {
              type = lib.types.nullOr lib.types.str;
              default = null;
              description = ''
                script to run before backing up the state dir
                This is for example useful for services that require an export of their state
                e.g. a database dump
              '';
            };

            # TODO: implement this
            #stopOnRestore = lib.mkOption {
            #  type = lib.types.listOf lib.types.str;
            #  default = [];
            #  description = ''
            #    List of services to stop before restoring the state dir from a backup

            #    Utilize this to stop services which currently access these folders or or other services affected by the restore
            #  '';
            #};

            preRestoreCommand = lib.mkOption {
              type = lib.types.nullOr lib.types.str;
              default = null;
              description = ''
                script to run before restoring the state dir from a backup

                Utilize this to stop services which currently access these folders
              '';
            };

            postRestoreCommand = lib.mkOption {
              type = lib.types.nullOr lib.types.str;
              default = null;
              description = ''
                script to restore the service after the state dir was restored from a backup

                Utilize this to start services which were previously stopped
              '';
            };
          };
        }
      )
    );
  };
}
