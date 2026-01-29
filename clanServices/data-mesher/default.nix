{
  clanLib,
  ...
}:
let
  inherit (clanLib) mkRemovedOption;
in
{
  _class = "clan.service";
  manifest.name = "data-mesher";
  manifest.description = "Set up data-mesher";
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    description = "A data-mesher node that distributes signed files across the Clan.";
    interface =
      { lib, ... }:
      {
        options = {

          logLevel = lib.mkOption {
            type = lib.types.enum [
              "fatal"
              "error"
              "warn"
              "info"
              "debug"
            ];
            default = "info";
            description = "Log level";
          };

          bootstrapNodes = lib.mkOption {
            type = lib.types.nullOr (lib.types.listOf lib.types.str);
            description = ''
              A list of bootstrap nodes that act as an initial gateway when joining
              the cluster.
            '';
            example = [
              "192.168.1.1:7946"
              "192.168.1.2:7946"
            ];
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

            # Removed in v2
            tld = mkRemovedOption "network.tld" "data-mesher v2 removed network-wide TLD. Use 'files' for file-based sync.";
            hostTTL = mkRemovedOption "network.hostTTL" "data-mesher v2 removed host TTL. Use 'files' for file-based sync.";
          };

          files = lib.mkOption {
            type = lib.types.attrsOf (lib.types.listOf lib.types.str);
            default = { };
            example = {
              "dns:sol" = [ "P6AE0lukf9/qmVglYrGPNYo5ZnpFrnqLeAzlCZF0lTk=" ];
              "config:app" = [
                "ZasdhiAVJTa5b2qG8ynWvdHqALUxC6Eg8pdn6RVXuQE="
                "1ru2QQ1eWV7yDlyfTTDEml3xTiacASYn0KprzknN8Pc="
              ];
            };
            description = ''
              A mapping of file names to lists of base64-encoded ED25519 public keys.
              Only files listed here can be uploaded or imported from other nodes,
              and they must be signed by one of the configured public keys.
            '';
          };

          # Removed in v2
          extraHostNames = mkRemovedOption "extraHostNames" "data-mesher v2 removed host name claims. Use 'files' for file-based sync.";
        };
      };
    perInstance =
      { settings, ... }:
      {
        nixosModule = {
          services.data-mesher = {
            enable = true;
            openFirewall = true;

            settings = {
              log_level = settings.logLevel;
              cluster = {
                port = settings.network.port;
                join_interval = "30s";
                push_pull_interval = "30s";
                interface = settings.network.interface;
                bootstrap_nodes = settings.bootstrapNodes;
              };

              http.port = 7331;
              http.interface = "lo";

              inherit (settings) files;
            };
          };
        };
      };
  };

  roles.admin = {
    description = "A data-mesher admin node that can sign files in the network.";
    interface = { };
    perInstance =
      { ... }:
      {
        nixosModule =
          { ... }:
          {
            assertions = [
              {
                assertion = false;
                message = "The 'admin' role was removed in data-mesher v2. Use the 'default' role instead. Data Mesher v2 uses file-based authorization instead of role-based signing.";
              }
            ];
          };
      };
  };

  roles.peer = {
    description = "A data-mesher peer node that connects to the network.";
    interface = { };
    perInstance =
      { ... }:
      {
        nixosModule =
          { ... }:
          {
            assertions = [
              {
                assertion = false;
                message = "The 'peer' role was removed in data-mesher v2. Use the 'default' role instead. Data Mesher v2 uses file-based authorization instead of role-based signing.";
              }
            ];
          };
      };
  };

  # Removed role from v1 - error when machines are assigned
  roles.signer = {
    description = "REMOVED: The signer role was removed in data-mesher v2. Use 'admin' or 'peer' instead.";
    interface = { };
    perInstance =
      { ... }:
      {
        nixosModule =
          { ... }:
          {
            assertions = [
              {
                assertion = false;
                message = "The 'signer' role was removed in data-mesher v2. Use 'admin' or 'peer' role instead. Data Mesher v2 uses file-based authorization instead of role-based signing.";
              }
            ];
          };
      };
  };
}
