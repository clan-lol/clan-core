{ config, lib, ... }:
{
  options.clan.networking.zerotier = {
    networkId = lib.mkOption {
      type = lib.types.str;
      description = ''
        zerotier networking id
      '';
    };
  };
  config = {
    systemd.network.networks.zerotier = {
      matchConfig.Name = "zt*";
      networkConfig = {
        LLMNR = true;
        LLDP = true;
        MulticastDNS = true;
        KeepConfiguration = "static";
      };
    };
    networking.firewall.allowedUDPPorts = [ 9993 ];
    networking.firewall.interfaces."zt+".allowedTCPPorts = [ 5353 ];
    networking.firewall.interfaces."zt+".allowedUDPPorts = [ 5353 ];
    services.zerotierone = {
      enable = true;
      joinNetworks = [ config.clan.networking.zerotier.networkId ];
    };
  };
}
