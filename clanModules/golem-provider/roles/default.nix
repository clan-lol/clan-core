{
  config,
  pkgs,
  lib,
  ...
}:
let
  cfg = config.clan.golem-provider;
  yagna = pkgs.callPackage ../../pkgs/yagna { };
  accountFlag = if cfg.account != null then "--account ${cfg.account}" else "";
in
{

  options.clan.golem-provider = {

    account = lib.mkOption {
      type = with lib.types; nullOr str;
      description = ''
        Ethereum address for payouts.

        Leave empty to automatically generate a new address upon first start.
      '';
      default = null;
    };
  };

  config = {
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
  };
}
