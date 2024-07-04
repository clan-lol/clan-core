{
  lib,
  pkgs,
  config,
  ...
}:
{
  # interface
  options.clan.core.state = lib.mkOption {
    description = ''
      Define state directories to backup and restore
    '';
    default = { };
    type = lib.types.attrsOf (
      lib.types.submodule (
        { name, config, ... }:
        {
          options = {
            name = lib.mkOption {
              type = lib.types.strMatching "^[a-zA-Z0-9_-]+$";
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

            preBackupScript = lib.mkOption {
              type = lib.types.nullOr lib.types.lines;
              default = null;
              description = ''
                script to run before backing up the state dir
                This is for example useful for services that require an export of their state
                e.g. a database dump
              '';
            };

            preBackupCommand = lib.mkOption {
              type = lib.types.nullOr lib.types.str;
              default = if config.preBackupScript == null then null else "pre-backup-${name}";
              readOnly = true;
              description = ''
                Use this command in backup providers. It contains the content of preBackupScript.
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

            preRestoreScript = lib.mkOption {
              type = lib.types.nullOr lib.types.lines;
              default = null;
              description = ''
                script to run before restoring the state dir from a backup

                Utilize this to stop services which currently access these folders
              '';
            };

            preRestoreCommand = lib.mkOption {
              type = lib.types.nullOr lib.types.str;
              default = if config.preRestoreScript == null then null else "pre-restore-${name}";
              readOnly = true;
              description = ''
                This command can be called to restore the state dir from a backup.
                It contains the content of preRestoreScript.
              '';
            };

            postRestoreScript = lib.mkOption {
              type = lib.types.nullOr lib.types.lines;
              default = null;
              description = ''
                script to restore the service after the state dir was restored from a backup

                Utilize this to start services which were previously stopped
              '';
            };

            postRestoreCommand = lib.mkOption {
              type = lib.types.nullOr lib.types.str;
              default = if config.postRestoreScript == null then null else "post-restore-${name}";
              readOnly = true;
              description = ''
                This command is called after a restore of the state dir from a backup.

                It contains the content of postRestoreScript.
              '';
            };
          };
        }
      )
    );
  };

  # defaults
  config.clan.core.state.HOME.folders = [ "/home" ];
  config.environment.systemPackages = lib.optional (config.clan.core.state != { }) (
    pkgs.runCommand "state-commands" { } ''
      ${builtins.concatStringsSep "\n" (
        builtins.map (state: ''
          writeShellScript() {
            local name=$1
            local content=$2
            printf "#!${pkgs.runtimeShell}\nset -eu -o pipefail\n%s" "$content" > $out/bin/$name
          }
          mkdir -p $out/bin/
          ${lib.optionalString (state.preBackupCommand != null) ''
            writeShellScript ${lib.escapeShellArg state.preBackupCommand} ${lib.escapeShellArg state.preBackupScript}
          ''}
          ${lib.optionalString (state.preRestoreCommand != null) ''
            writeShellScript ${lib.escapeShellArg state.preRestoreCommand} ${lib.escapeShellArg state.preRestoreScript}
          ''}
          ${lib.optionalString (state.postRestoreCommand != null) ''
            writeShellScript ${lib.escapeShellArg state.postRestoreCommand} ${lib.escapeShellArg state.postRestoreScript}
          ''}
          find $out/bin/ -type f -print0 | xargs --no-run-if-empty -0 chmod 755
        '') (builtins.attrValues config.clan.core.state)
      )}
    ''
  );
}
