{ config, lib, pkgs, ... }:
let
  cfg = config.clan.networking.meshnamed;
in
{
  options.clan.networking.meshnamed = {
    enable = (lib.mkEnableOption "meshnamed") // {
      default = config.clan.networking.meshnamed.networks != { };
    };
    listenAddress = lib.mkOption {
      type = lib.types.str;
      default = "fd66:29e9:f422:8dfe:beba:68ec:bd09:7876";
      description = lib.mdDoc ''
        The address to listen on.
      '';
    };
    networks = lib.mkOption {
      default = { };
      type = lib.types.attrsOf (lib.types.submodule ({ name, ... }: {
        options = {
          name = lib.mkOption {
            default = name;
            type = lib.types.str;
            example = "my-network";
            description = lib.mdDoc ''
              The name of the network.
            '';
          };
          subnet = lib.mkOption {
            type = lib.types.str;
            example = "fd43:7def:4b50:28d0:4e99:9347:3035:17ef/88";
            description = lib.mdDoc ''
              The subnet to use for the mesh network.
            '';
          };
        };
      }));
    };
  };
  config = lib.mkIf config.clan.networking.meshnamed.enable {
    # we assign this random source address to bind meshnamed to.
    systemd.network.netdevs."08-meshnamed" = {
      netdevConfig = {
        Name = "meshnamed";
        Kind = "dummy";
      };
    };
    systemd.network.networks."08-meshnamed" = {
      matchConfig.Name = "meshnamed";
      networkConfig = {
        Address = [ "${cfg.listenAddress}/128" ];
        DNS = [ config.clan.networking.meshnamed.listenAddress ];
        Domains = [ "~${lib.concatMapStringsSep "," (network: network.name) (builtins.attrValues config.clan.networking.meshnamed.networks)}" ];
      };
    };

    # for convenience, so we can debug with dig
    networking.extraHosts = ''
      ${cfg.listenAddress} meshnamed
    '';

    networking.networkmanager.unmanaged = [ "interface-name:meshnamed" ];

    systemd.services.meshnamed =
      let
        networks = lib.concatMapStringsSep "," (network: "${network.name}=${network.subnet}")
          (builtins.attrValues config.clan.networking.meshnamed.networks);
      in
      {
        # fix container test
        after = [ "network.target" ] ++ lib.optional config.boot.isContainer "sys-devices-virtual-net-meshnamed.device";
        bindsTo = lib.optional (!config.boot.isContainer) "sys-devices-virtual-net-meshnamed.device";
        wantedBy = [ "multi-user.target" ];
        serviceConfig = {
          Type = "simple";
          ExecStart = "${pkgs.callPackage ../../../pkgs/meshname/default.nix { }}/bin/meshnamed -networks ${networks} -listenaddr [${cfg.listenAddress}]:53";

          # to bind port 53
          AmbientCapabilities = [ "CAP_NET_BIND_SERVICE" ];
          DynamicUser = true;
        };
      };
  };
}
