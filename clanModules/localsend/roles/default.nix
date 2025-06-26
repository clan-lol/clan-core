{
  config,
  pkgs,
  lib,
  ...
}:

let
  cfg = config.clan.localsend;
in
{
  # Integration can be improved, if the following issues get implemented:
  # - cli frontend: https://github.com/localsend/localsend/issues/11
  # - ipv6 support: https://github.com/localsend/localsend/issues/549
  options.clan.localsend = {

    displayName = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = "The name that localsend will use to display your instance.";
    };

    package = lib.mkPackageOption pkgs "localsend" { };

    ipv4Addr = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      example = "192.168.56.2/24";
      description = "Optional IPv4 address for ZeroTier network.";
    };
  };

  imports = [
    (lib.mkRemovedOptionModule [
      "clan"
      "localsend"
      "enable"
    ] "Importing the module will already enable the service.")
  ];
  config = {
    warnings = [
      "The clan.localsend module is deprecated and will be removed on 2025-07-15.
      Please migrate to user-maintained configuration or the new equivalent clan services
      (https://docs.clan.lol/reference/clanServices)."
    ];

    clan.core.state.localsend.folders = [
      "/var/localsend"
    ];
    environment.systemPackages = [
      (pkgs.callPackage ./localsend-ensure-config {
        localsend = config.clan.localsend.package;
        alias = config.clan.localsend.displayName;
      })
    ];

    networking.firewall.interfaces."zt+".allowedTCPPorts = [ 53317 ];
    networking.firewall.interfaces."zt+".allowedUDPPorts = [ 53317 ];

    #TODO: This is currently needed because there is no ipv6 multicasting support yet
    systemd.network.networks = lib.mkIf (cfg.ipv4Addr != null) {
      "09-zerotier" = {
        networkConfig = {
          Address = cfg.ipv4Addr;
        };
      };
    };
  };
}
