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
              type = lib.types.strMatching "^[a-zA-Z0-9._-]+$";
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
                config.clanCore.facts.services.borgbackup.secret."borgbackup.ssh".path
              } -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
              defaultText = "ssh -i \${config.clanCore.facts.services.borgbackup.secret.\"borgbackup.ssh\".path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
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
        passCommand = "cat ${config.clanCore.facts.services.borgbackup.secret."borgbackup.repokey".path}";
      };

      prune.keep = {
        within = "1d"; # Keep all archives from the last day
        daily = 7;
        weekly = 4;
        monthly = 0;
      };
    }) cfg.destinations;

    clanCore.facts.services.borgbackup = {
      public."borgbackup.ssh.pub" = { };
      secret."borgbackup.ssh" = { };
      secret."borgbackup.repokey" = { };
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

    environment.systemPackages = [
      (pkgs.writeShellScriptBin "borgbackup-create" ''
        set -efu -o pipefail
        ${lib.concatMapStringsSep "\n" (dest: ''
          systemctl start borgbackup-job-${dest.name}
        '') (lib.attrValues cfg.destinations)}
      '')
      (pkgs.writeShellScriptBin "borgbackup-list" ''
        set -efu
        (${
          lib.concatMapStringsSep "\n" (
            dest:
            # we need yes here to skip the changed url verification
            ''yes y | borg-job-${dest.name} list --json | jq '[.archives[] | {"name": ("${dest.name}::${dest.repo}::" + .name)}]' ''
          ) (lib.attrValues cfg.destinations)
        }) | ${pkgs.jq}/bin/jq -s 'add'
      '')
      (pkgs.writeShellScriptBin "borgbackup-restore" ''
        set -efux
        cd /
        IFS=':' read -ra FOLDER <<< "$FOLDERS"
        job_name=$(echo "$NAME" | ${pkgs.gawk}/bin/awk -F'::' '{print $1}')
        backup_name=''${NAME#"$job_name"::}
        if ! command -v borg-job-"$job_name" &> /dev/null; then
          echo "borg-job-$job_name not found: Backup name is invalid" >&2
          exit 1
        fi
        yes y | borg-job-"$job_name" extract --list "$backup_name" "''${FOLDER[@]}"
      '')
    ];

    clanCore.backups.providers.borgbackup = {
      list = "borgbackup-list";
      create = "borgbackup-create";
      restore = "borgbackup-restore";
    };
  };
}
