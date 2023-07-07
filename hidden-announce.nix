{ config, lib, pkgs, ... }:
{
  options.hidden-announce = {
    enable = lib.mkEnableOption "hidden-announce";
    script = lib.mkOption {
      type = lib.types.package;
      default = pkgs.writers.writeDash "test-output";
      description = ''
        script to run when the hidden tor service was started and they hostname is known.
        takes the hostname as $1
      '';
    };
  };

  config = lib.mkIf config.hidden-announce.enable {
    services.tor = {
      enable = true;
      relay.onionServices.hidden-ssh = {
        version = 3;
        map = [{
          port = 22;
          target.port = 22;
        }];
      };
      client.enable = true;
    };
    systemd.services.hidden-ssh-announce = {
      description = "irc announce hidden ssh";
      after = [ "tor.service" "network-online.target" ];
      wants = [ "tor.service" ];
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        # ${pkgs.tor}/bin/torify
        ExecStart = pkgs.writers.writeDash "announce-hidden-service" ''
          set -efu
          until test -e ${config.services.tor.settings.DataDirectory}/onion/hidden-ssh/hostname; do
            echo "still waiting for ${config.services.tor.settings.DataDirectory}/onion/hidden-ssh/hostname"
            sleep 1
          done

          ${config.hidden-announce.script} "$(cat ${config.services.tor.settings.DataDirectory}/onion/hidden-ssh/hostname)"
        '';
        PrivateTmp = "true";
        User = "tor";
        Type = "oneshot";
      };
    };
  };
}
