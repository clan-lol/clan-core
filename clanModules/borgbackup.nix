{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.clan.borgbackup;
in
{
  options.clan.borgbackup.destinations = lib.mkOption {
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
            repo = lib.mkOption {
              type = lib.types.str;
              description = "the borgbackup repository to backup to";
            };
            rsh = lib.mkOption {
              type = lib.types.str;
              default = "ssh -i ${
                config.clanCore.secrets.borgbackup.secrets."borgbackup.ssh".path
              } -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
              description = "the rsh to use for the backup";
            };
          };
        }
      )
    );
    default = { };
    description = ''
      destinations where the machine should be backuped to
    '';
  };

  imports = [
    (lib.mkRemovedOptionModule [
      "clan"
      "borgbackup"
      "enable"
    ] "Just define clan.borgbackup.destinations to enable it")
  ];

  config = lib.mkIf (cfg.destinations != { }) {
    services.borgbackup.jobs = lib.mapAttrs (_: dest: {
      paths = lib.flatten (map (state: state.folders) (lib.attrValues config.clanCore.state));
      exclude = [ "*.pyc" ];
      repo = dest.repo;
      environment.BORG_RSH = dest.rsh;
      compression = "auto,zstd";
      startAt = "*-*-* 01:00:00";
      persistentTimer = true;
      preHook = ''
        set -x
      '';

      encryption = {
        mode = "repokey";
        passCommand = "cat ${config.clanCore.secrets.borgbackup.secrets."borgbackup.repokey".path}";
      };

      prune.keep = {
        within = "1d"; # Keep all archives from the last day
        daily = 7;
        weekly = 4;
        monthly = 0;
      };
    }) cfg.destinations;

    clanCore.secrets.borgbackup = {
      facts."borgbackup.ssh.pub" = { };
      secrets."borgbackup.ssh" = { };
      secrets."borgbackup.repokey" = { };
      generator.path = [
        pkgs.openssh
        pkgs.coreutils
        pkgs.xkcdpass
      ];
      generator.script = ''
        ssh-keygen -t ed25519 -N "" -f "$secrets"/borgbackup.ssh
        mv "$secrets"/borgbackup.ssh.pub "$facts"/borgbackup.ssh.pub
        xkcdpass -n 4 -d - > "$secrets"/borgbackup.repokey
      '';
    };

    environment.systemPackages = [ pkgs.jq ];

    clanCore.backups.providers.borgbackup = {
      # TODO list needs to run locally or on the remote machine
      list = ''
        set -efu
        # we need yes here to skip the changed url verification
        ${
          lib.concatMapStringsSep "\\\n" (
            dest:
            ''yes y | borg-job-${dest.name} list --json | jq '[.archives[] | {"name": ("${dest.repo}::" + .name), "job_name": "${dest.name}"}]' ''
          ) (lib.attrValues cfg.destinations)
        } | jq -s 'add'
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
        yes y | borg-job-"$JOB_NAME" extract --list "$NAME" "''${FOLDER[@]}"
      '';
    };
  };
}
