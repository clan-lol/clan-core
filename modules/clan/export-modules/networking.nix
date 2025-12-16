{ lib, ... }:
{
  options = {
    priority = lib.mkOption {
      type = lib.types.int;
      default = 1000;
      description = ''
        priority with which this network should be tried.
        higher priority means it gets used earlier in the chain
      '';
    };
    module = lib.mkOption {
      # type = lib.types.enum [
      #   "clan_lib.network.direct"
      #   "clan_lib.network.tor"
      # ];
      type = lib.types.str;
      default = "clan_lib.network.direct";
      description = ''
        the technology this network uses to connect to the target
        This is used for userspace networking with socks proxies.
      '';
    };
  };
}
