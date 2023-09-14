{ config, lib, ... }:
{
  options.clan.networking = {
    deploymentAddress = lib.mkOption {
      description = ''
        The target SSH node for deployment.

        By default, the node's attribute name will be used.
        If set to null, only local deployment will be supported.
      '';
      type = lib.types.nullOr lib.types.str;
      default = "root@${config.networking.hostName}";
    };
  };
}
