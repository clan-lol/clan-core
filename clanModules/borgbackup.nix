{ config, lib, pkgs, ... }:
let
  cfg = config.clan.borgbackup;
in
{
  options.clan.borgbackup = {
    enable = lib.mkEnableOption "backups with borgbackup";
    destinations = lib.mkOption {
      type = lib.types.attrsOf (lib.types.submodule ({ name, ... }: {
        options = {
          name = lib.mkOption {
            type = lib.types.str;
            default = name;
            description = "the name of the backup job";
          };
          repo = lib.mkOption {
            type = lib.types.str;
            description = "the borgbackup repository to backup to";
          };
          rsh = lib.mkOption {
            type = lib.types.str;
            default = "ssh -i ${config.clanCore.secrets.borgbackup.secrets."borgbackup.ssh".path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
            description = "the rsh to use for the backup";
          };

        };
      }));
      description = ''
        destinations where the machine should be backuped to
      '';
    };
  };
  config = lib.mkIf cfg.enable {
    services.borgbackup.jobs = lib.mapAttrs
      (_: dest: {
        paths = lib.flatten (map (state: state.folders) (lib.attrValues config.clanCore.state));
        exclude = [
          "*.pyc"
        ];
        repo = dest.repo;
        environment.BORG_RSH = dest.rsh;
        encryption.mode = "none";
        compression = "auto,zstd";
        startAt = "*-*-* 01:00:00";
        preHook = ''
          set -x
        '';

        prune.keep = {
          within = "1d"; # Keep all archives from the last day
          daily = 7;
          weekly = 4;
          monthly = 0;
        };
      })
      cfg.destinations;

    clanCore.secrets.borgbackup = {
      facts."borgbackup.ssh.pub" = { };
      secrets."borgbackup.ssh" = { };
      generator.path = [ pkgs.openssh pkgs.coreutils ];
      generator.script = ''
        ssh-keygen -t ed25519 -N "" -f "$secrets"/borgbackup.ssh
        mv "$secrets"/borgbackup.ssh.pub "$facts"/borgbackup.ssh.pub
      '';
    };

    clanCore.backups.providers.borgbackup = {
      # TODO list needs to run locally or on the remote machine
      list = ''
        ${lib.concatMapStringsSep "\n" (dest: ''
          # we need yes here to skip the changed url verification
          yes y | borg-job-${dest.name} list --json | jq -r '. + {"job-name": "${dest.name}"}'
        '') (lib.attrValues cfg.destinations)}
      '';
      create = ''
        ${lib.concatMapStringsSep "\n" (dest: ''
          systemctl start borgbackup-job-${dest.name}
        '') (lib.attrValues cfg.destinations)}
      '';

      restore = ''
        set -efu
        cd /
        IFS=';' read -ra FOLDER <<< "$FOLDERS"
        yes y | borg-job-"$JOB" extract --list "$LOCATION"::"$ARCHIVE_ID" "''${FOLDER[@]}"
      '';
    };
  };
}
