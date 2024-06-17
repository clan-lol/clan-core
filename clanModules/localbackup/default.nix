{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.clan.localbackup;
  uniqueFolders = lib.unique (
    lib.flatten (lib.mapAttrsToList (_name: state: state.folders) config.clan.core.state)
  );
  rsnapshotConfig = target: ''
    config_version	1.2
    snapshot_root	${target.directory}
    sync_first	1
    cmd_cp	${pkgs.coreutils}/bin/cp
    cmd_rm	${pkgs.coreutils}/bin/rm
    cmd_rsync	${pkgs.rsync}/bin/rsync
    cmd_ssh	${pkgs.openssh}/bin/ssh
    cmd_logger	${pkgs.inetutils}/bin/logger
    cmd_du	${pkgs.coreutils}/bin/du
    cmd_rsnapshot_diff	${pkgs.rsnapshot}/bin/rsnapshot-diff

    ${lib.optionalString (target.postBackupHook != null) ''
      cmd_postexec	${pkgs.writeShellScript "postexec.sh" ''
        set -efu -o pipefail
        ${target.postBackupHook}
      ''}
    ''}
    retain	snapshot	${builtins.toString config.clan.localbackup.snapshots}
    ${lib.concatMapStringsSep "\n" (folder: ''
      backup	${folder}	${config.networking.hostName}/
    '') uniqueFolders}
  '';
in
{
  options.clan.localbackup = {
    targets = lib.mkOption {
      type = lib.types.attrsOf (
        lib.types.submodule (
          { name, ... }:
          {
            options = {
              name = lib.mkOption {
                type = lib.types.strMatching "^[a-zA-Z0-9._-]+$";
                default = name;
                description = "the name of the backup job";
              };
              directory = lib.mkOption {
                type = lib.types.str;
                description = "the directory to backup";
              };
              mountpoint = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
                description = "mountpoint of the directory to backup. If set, the directory will be mounted before the backup and unmounted afterwards";
              };
              preMountHook = lib.mkOption {
                type = lib.types.nullOr lib.types.lines;
                default = null;
                description = "Shell commands to run before the directory is mounted";
              };
              postMountHook = lib.mkOption {
                type = lib.types.nullOr lib.types.lines;
                default = null;
                description = "Shell commands to run after the directory is mounted";
              };
              preUnmountHook = lib.mkOption {
                type = lib.types.nullOr lib.types.lines;
                default = null;
                description = "Shell commands to run before the directory is unmounted";
              };
              postUnmountHook = lib.mkOption {
                type = lib.types.nullOr lib.types.lines;
                default = null;
                description = "Shell commands to run after the directory is unmounted";
              };
              preBackupHook = lib.mkOption {
                type = lib.types.nullOr lib.types.lines;
                default = null;
                description = "Shell commands to run before the backup";
              };
              postBackupHook = lib.mkOption {
                type = lib.types.nullOr lib.types.lines;
                default = null;
                description = "Shell commands to run after the backup";
              };
            };
          }
        )
      );
      default = { };
      description = "List of directories where backups are stored";
    };

    snapshots = lib.mkOption {
      type = lib.types.int;
      default = 20;
      description = "Number of snapshots to keep";
    };
  };

  config =
    let
      mountHook = target: ''
        if [[ -x /run/current-system/sw/bin/localbackup-mount-${target.name} ]]; then
          /run/current-system/sw/bin/localbackup-mount-${target.name}
        fi
        if [[ -x /run/current-system/sw/bin/localbackup-unmount-${target.name} ]]; then
          trap "/run/current-system/sw/bin/localbackup-unmount-${target.name}" EXIT
        fi
      '';
    in
    lib.mkIf (cfg.targets != { }) {
      environment.systemPackages =
        [
          (pkgs.writeShellScriptBin "localbackup-create" ''
            set -efu -o pipefail
            export PATH=${
              lib.makeBinPath [
                pkgs.rsnapshot
                pkgs.coreutils
                pkgs.util-linux
              ]
            }
            ${lib.concatMapStringsSep "\n" (target: ''
              ${mountHook target}
              set -x
              echo "Creating backup '${target.name}'"

              ${lib.optionalString (target.preBackupHook != null) ''
                (
                  ${target.preBackupHook}
                )
              ''}

              declare -A preCommandErrors
              ${lib.concatMapStringsSep "\n" (
                state:
                lib.optionalString (state.preBackupCommand != null) ''
                  echo "Running pre-backup command for ${state.name}"
                  if ! ( ${state.preBackupCommand} ) then
                    preCommandErrors["${state.name}"]=1
                  fi
                ''
              ) (builtins.attrValues config.clan.core.state)}

              rsnapshot -c "${pkgs.writeText "rsnapshot.conf" (rsnapshotConfig target)}" sync
              rsnapshot -c "${pkgs.writeText "rsnapshot.conf" (rsnapshotConfig target)}" snapshot
            '') (builtins.attrValues cfg.targets)}'')
          (pkgs.writeShellScriptBin "localbackup-list" ''
            set -efu -o pipefail
            export PATH=${
              lib.makeBinPath [
                pkgs.jq
                pkgs.findutils
                pkgs.coreutils
                pkgs.util-linux
              ]
            }
            (${
              lib.concatMapStringsSep "\n" (target: ''
                (
                  ${mountHook target}
                  find ${lib.escapeShellArg target.directory} -mindepth 1 -maxdepth 1 -name "snapshot.*" -print0 -type d \
                    | jq -Rs 'split("\u0000") | .[] | select(. != "") | { "name": ("${target.name}::" + .)}'
                )
              '') (builtins.attrValues cfg.targets)
            }) | jq -s .
          '')
          (pkgs.writeShellScriptBin "localbackup-restore" ''
            set -efu -o pipefail
            export PATH=${
              lib.makeBinPath [
                pkgs.rsync
                pkgs.coreutils
                pkgs.util-linux
                pkgs.gawk
              ]
            }
            if [[ "''${NAME:-}" == "" ]]; then
              echo "No backup name given via NAME environment variable"
              exit 1
            fi
            if [[ "''${FOLDERS:-}" == "" ]]; then
              echo "No folders given via FOLDERS environment variable"
              exit 1
            fi
            name=$(awk -F'::' '{print $1}' <<< $NAME)
            backupname=''${NAME#$name::}

            if command -v localbackup-mount-$name; then
              localbackup-mount-$name
            fi
            if command -v localbackup-unmount-$name; then
              trap "localbackup-unmount-$name" EXIT
            fi

            if [[ ! -d $backupname ]]; then
              echo "No backup found $backupname"
              exit 1
            fi

            IFS=':' read -ra FOLDER <<< "''$FOLDERS"
            for folder in "''${FOLDER[@]}"; do
              mkdir -p "$folder"
              rsync -a "$backupname/${config.networking.hostName}$folder/" "$folder"
            done
          '')
        ]
        ++ (lib.mapAttrsToList (
          name: target:
          pkgs.writeShellScriptBin ("localbackup-mount-" + name) ''
            set -efu -o pipefail
            ${lib.optionalString (target.preMountHook != null) target.preMountHook}
            ${lib.optionalString (target.mountpoint != null) ''
              if ! ${pkgs.util-linux}/bin/mountpoint -q ${lib.escapeShellArg target.mountpoint}; then
                ${pkgs.util-linux}/bin/mount -o X-mount.mkdir ${lib.escapeShellArg target.mountpoint}
              fi
            ''}
            ${lib.optionalString (target.postMountHook != null) target.postMountHook}
          ''
        ) cfg.targets)
        ++ lib.mapAttrsToList (
          name: target:
          pkgs.writeShellScriptBin ("localbackup-unmount-" + name) ''
            set -efu -o pipefail
            ${lib.optionalString (target.preUnmountHook != null) target.preUnmountHook}
            ${lib.optionalString (
              target.mountpoint != null
            ) "${pkgs.util-linux}/bin/umount ${lib.escapeShellArg target.mountpoint}"}
            ${lib.optionalString (target.postUnmountHook != null) target.postUnmountHook}
          ''
        ) cfg.targets;

      clan.core.backups.providers.localbackup = {
        # TODO list needs to run locally or on the remote machine
        list = "localbackup-list";
        create = "localbackup-create";
        restore = "localbackup-restore";
      };
    };
}
