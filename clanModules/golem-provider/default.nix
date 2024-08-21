{ config, pkgs, ... }:
let
  cfg = config.clan.golem-provider;
  yagna = pkgs.callPackage ../../pkgs/yagna { };
  accountFlag = if cfg.account != null then "--account ${cfg.account}" else "";
in
{
  imports = [ ./interface.nix ];

  users.users.golem = {
    isSystemUser = true;
    home = "/var/lib/golem";
    group = "golem";
    createHome = true;
  };

  users.groups.golem = { };

  environment.systemPackages = [ yagna ];

  systemd.services.golem-provider = {
    description = "Golem Provider";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    serviceConfig = {
      Type = "simple";
      ExecStart = "${yagna}/bin/golemsp run --no-interactive ${accountFlag}";
      Restart = "always";
      RestartSec = "5";
      User = "golem";
      Group = "golem";
    };
  };
}
