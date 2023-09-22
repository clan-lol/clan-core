{ config, lib, ... }:
{
  options.clan.networking = {
    deploymentAddress = lib.mkOption {
      description = ''
        The target SSH node for deployment.

        By default, the node's attribute name will be used.
        If set to null, only local deployment will be supported.

        format: user@host:port&SSH_OPTION=SSH_VALUE
        examples:
          - machine.example.com
          - user@machine2.example.com
          - root@example.com:2222&IdentityFile=/path/to/private/key
      '';
      type = lib.types.nullOr lib.types.str;
      default = "root@${config.networking.hostName}";
    };
  };
}
