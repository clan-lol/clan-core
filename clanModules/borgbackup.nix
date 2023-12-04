{ config, lib, ... }:
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
            default = "";
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

    clanCore.backups.providers.borgbackup = {
      list = ''
        ${lib.concatMapStringsSep "\n" (dest: ''
          (
            export BORG_REPO=${lib.escapeShellArg dest.repo}
            export BORG_RSH=${lib.escapeShellArg dest.rsh}
            ${lib.getExe config.services.borgbackup.package} list
          )
        '') (lib.attrValues cfg.destinations)}
      '';
      start = ''
        ssh ${config.clan.networking.deploymentAddress} -- '
          ${lib.concatMapStringsSep "\n" (dest: ''
            systemctl start borgbackup-job-${dest.name}
          '') (lib.attrValues cfg.destinations)}
        '
      '';

      restore = ''
      '';
    };
  };
}
