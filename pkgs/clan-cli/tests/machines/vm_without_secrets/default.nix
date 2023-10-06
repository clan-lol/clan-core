{ lib, ... }: {
  clan.networking.deploymentAddress = "__CLAN_DEPLOYMENT_ADDRESS__";
  system.stateVersion = lib.version;
  clan.virtualisation.graphics = false;

  networking.useDHCP = false;

  systemd.services.shutdown-after-boot = {
    enable = true;
    wantedBy = [ "multi-user.target" ];
    after = [ "multi-user.target" ];
    script = ''
      #!/usr/bin/env bash
      shutdown -h now
    '';
  };
}
