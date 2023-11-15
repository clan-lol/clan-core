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
  config = {
    # conflicts with systemd-resolved
    networking.useHostResolvConf = false;

    # The notion of "online" is a broken concept
    # https://github.com/systemd/systemd/blob/e1b45a756f71deac8c1aa9a008bd0dab47f64777/NEWS#L13
    systemd.services.NetworkManager-wait-online.enable = false;
    systemd.network.wait-online.enable = false;

    # Use networkd instead of the pile of shell scripts
    networking.useNetworkd = lib.mkDefault true;
    networking.useDHCP = lib.mkDefault false;
  };
}
