{ pkgs, ... }:
{
  systemd.services.dummy-service = {
    enable = true;
    description = "Dummy service";
    wantedBy = [ "multi-user.target" ];
    serviceConfig = {
      Type = "oneshot";
      ExecStart = "${pkgs.coreutils}/bin/true";
      RemainAfterExit = true;
    };
  };
}
