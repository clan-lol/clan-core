{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.clan.localbackup;
  rsnapshotConfig = target: states: ''
    config_version	1.2
    snapshot_root	${target}
    sync_first	1
    cmd_cp	${pkgs.coreutils}/bin/cp
    cmd_rm	${pkgs.coreutils}/bin/rm
    cmd_rsync	${pkgs.rsync}/bin/rsync
    cmd_ssh	${pkgs.openssh}/bin/ssh
    cmd_logger	${pkgs.inetutils}/bin/logger
    cmd_du	${pkgs.coreutils}/bin/du
    cmd_rsnapshot_diff	${pkgs.rsnapshot}/bin/rsnapshot-diff
    retain	snapshot	${builtins.toString config.clan.localbackup.snapshots}
    ${lib.concatMapStringsSep "\n" (state: ''
      ${lib.concatMapStringsSep "\n" (folder: ''
        backup	${folder}	${config.networking.hostName}/
      '') state.folders}
    '') states}
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
                type = lib.types.str;
                default = name;
                description = "the name of the backup job";
              };
              directory = lib.mkOption {
                type = lib.types.str;
                description = "the directory to backup";
              };
              mountpoint = lib.mkOption {
                type = lib.types.nullOr (lib.types.strMatching "^[a-zA-Z0-9./_-]+$");
                default = null;
                description = "mountpoint of the directory to backup. If set, the directory will be mounted before the backup and unmounted afterwards";
              };
            };
          }
        )
      );
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
      setupMount =
        mountpoint:
        lib.optionalString (mountpoint != null) ''
          mkdir -p ${lib.escapeShellArg mountpoint}
          if mountpoint -q ${lib.escapeShellArg mountpoint}; then
            umount ${lib.escapeShellArg mountpoint}
          fi
          mount ${lib.escapeShellArg mountpoint}
          trap "umount ${lib.escapeShellArg mountpoint}" EXIT
        '';
    in
    lib.mkIf (cfg.targets != [ ]) {
      environment.systemPackages = [
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
            (
              echo "Creating backup '${target.name}'"
              ${setupMount target.mountpoint}
              rsnapshot -c "${pkgs.writeText "rsnapshot.conf" (rsnapshotConfig target.directory (lib.attrValues config.clanCore.state))}" sync
              rsnapshot -c "${pkgs.writeText "rsnapshot.conf" (rsnapshotConfig target.directory (lib.attrValues config.clanCore.state))}" snapshot
            )
          '') (builtins.attrValues cfg.targets)}
        '')
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
                ${setupMount target.mountpoint}
                find ${lib.escapeShellArg target.directory} -mindepth 1 -maxdepth 1 -name "snapshot.*" -print0 -type d \
                  | jq -Rs 'split("\u0000") | .[] | select(. != "") | { "name": ("${target.mountpoint}::" + .)}'
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
          mountpoint=$(awk -F'::' '{print $1}' <<< $NAME)
          backupname=''${NAME#$mountpoint::}

          mkdir -p "$mountpoint"
          if mountpoint -q "$mountpoint"; then
            umount "$mountpoint"
          fi
          mount "$mountpoint"
          trap "umount $mountpoint" EXIT

          IFS=';' read -ra FOLDER <<< "$FOLDERS"
          for folder in "''${FOLDER[@]}"; do
            rsync -a "$backupname/${config.networking.hostName}$folder/" "$folder"
          done
        '')
      ];

      clanCore.backups.providers.localbackup = {
        # TODO list needs to run locally or on the remote machine
        list = "localbackup-list";
        create = "localbackup-create";
        restore = "localbackup-restore";
      };
    };
}
