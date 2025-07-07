{ ... }:
let
  sharedInterface =
    { lib, ... }:
    {
      options = {
        bootstrapNodes = lib.mkOption {
          type = lib.types.nullOr (lib.types.attrsOf lib.types.str);
          # the default bootstrap nodes are any machines with the admin or signers role
          # we iterate through those machines, determining an IP address for them based on their VPN
          # currently only supports zerotier
          # default = builtins.foldl' (
          #   urls: name:
          #   let
          #     ipPath = "${config.clan.core.settings.directory}/vars/per-machine/${name}/zerotier/zerotier-ip/value";
          #   in
          #   if builtins.pathExists ipPath then
          #     let
          #       ip = builtins.readFile ipPath;
          #     in
          #     urls ++ [ "[${ip}]:${builtins.toString settings.network.port}" ]
          #   else
          #     urls
          # ) [ ] (dmLib.machines config).bootstrap;
          description = ''
            A list of bootstrap nodes that act as an initial gateway when joining
            the cluster.
          '';
          example = {
            "node1" = "192.168.1.1:7946";
            "node2" = "192.168.1.2:7946";
          };
        };

        network = {
          interface = lib.mkOption {
            type = lib.types.str;
            description = ''
              The interface over which cluster communication should be performed.
              All the ip addresses associate with this interface will be part of
              our host claim, including both ipv4 and ipv6.

              This should be set to an internal/VPN interface.
            '';
            example = "tailscale0";
          };

          port = lib.mkOption {
            type = lib.types.port;
            default = 7946;
            description = ''
              Port to listen on for cluster communication.
            '';
          };
        };
      };
    };
in
{
  _class = "clan.service";
  manifest.name = "data-mesher";
  manifest.description = "Set up data-mesher";
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.admin = {
    interface =
      { lib, ... }:
      {

        imports = [ sharedInterface ];

        options = {

          network = {
            tld = lib.mkOption {
              type = lib.types.str;
              default = "clan";
              description = "Top level domain to use for the network";
            };

            hostTTL = lib.mkOption {
              type = lib.types.str;
              default = "${toString (24 * 28)}h";
              example = "24h";
              description = "The TTL for hosts in the network, in the form of a Go time.Duration";
            };
          };
        };
      };
    perInstance =
      { settings, roles, ... }:
      {
        nixosModule = {
          imports = [
            ./admin.nix
            ./shared.nix
          ];
          _module.args = { inherit settings roles; };
        };
      };
  };

  roles.signer = {
    interface =
      { ... }:
      {
        imports = [ sharedInterface ];
      };
    perInstance =
      { settings, roles, ... }:
      {
        nixosModule = {
          imports = [
            ./signer.nix
            ./shared.nix
          ];
          _module.args = { inherit settings roles; };
        };
      };
  };

  roles.peer = {
    interface =
      { ... }:
      {
        imports = [ sharedInterface ];
      };
    perInstance =
      { settings, roles, ... }:
      {
        nixosModule = {
          imports = [
            ./peer.nix
            ./shared.nix
          ];
          _module.args = { inherit settings roles; };
        };
      };
  };

}
