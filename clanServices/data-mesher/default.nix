{
  clanLib,
  lib,
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

          port = lib.mkOption {
            type = lib.types.port;
            default = 7946;
            description = ''
              Port to listen on for cluster communication.
            '';
          };

          extraBootstrapPeers = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            default = [ ];
            description = ''
              Additional bootstrap peers that act as an initial gateway when joining
              the cluster. These are merged with machines from the 'bootstrap' role.

              They must be libp2p multi addresses: https://libp2p.io/guides/addressing
            '';
            example = [
              "/ip4/192.168.1.1/tcp/7946/p2p/12D3KooWHs5NXo2CPFvFT6cdsu8eSkfggNtfqTtKBVojHY7En86i"
              "/ip4/192.168.1.2/tcp/7946/p2p/12D3KooWDSrQ6xLqFmS44bZKXDujBmTDNu7BQS9HmDz6FRS52CyN"
            ];
          };

          interfaces = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            default = [ ];
            description = ''
              We will bind to each each interface listed, listening for connections on `cluster.port`.
              If no interfaces are provided, we will bind to all available.
            '';
            example = [
              "eth1"
              "tailscale0"
            ];
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

          network = {
            interface = mkRemovedOption "network.interface" "Use 'interfaces' instead.";

            port = mkRemovedOption "network.port" "Use 'port' instead.";

            # Removed in v2
            tld = mkRemovedOption "network.tld" "data-mesher v2 removed network-wide TLD. Use 'files' for file-based sync.";
            hostTTL = mkRemovedOption "network.hostTTL" "data-mesher v2 removed host TTL. Use 'files' for file-based sync.";
          };

          extraHostNames = mkRemovedOption "extraHostNames" "data-mesher v2 removed host name claims. Use 'files' for file-based sync.";
        };
      };
    perInstance =
      {
        settings,
        exports,
        roles,
        ...
      }:
      let
        # Collect all export values
        allExports = lib.attrValues exports;

        # Extract and merge dataMesher.files from all exports
        exportedFiles = lib.foldl' (
          acc: exportValue:
          let
            dmFiles =
              if exportValue ? dataMesher && exportValue.dataMesher != null then
                exportValue.dataMesher.files
              else
                { };
          in
          lib.foldlAttrs (
            innerAcc: fileName: keys:
            innerAcc // { ${fileName} = (innerAcc.${fileName} or [ ]) ++ keys; }
          ) acc dmFiles
        ) { } allExports;

        # Merge with manually configured files (keys are concatenated)
        mergedFiles = lib.foldlAttrs (
          acc: fileName: keys:
          acc // { ${fileName} = (acc.${fileName} or [ ]) ++ keys; }
        ) exportedFiles settings.files;
      in
      {
        nixosModule = (
          { config, ... }:
          let
            dmConfig = config.services.data-mesher;

            # Bootstrap nodes derived from machines in the 'bootstrap' role, excluding ourselves
            bootstrapPeersFromRole = lib.mapAttrsToList (
              name: _:
              let
                peerID = clanLib.getPublicValue {
                  flake = config.clan.core.settings.directory;
                  machine = name;
                  generator = "data-mesher-node-identity";
                  file = "peer.id";
                };
              in
              "/dns/${name}.${config.clan.core.settings.domain}/tcp/${toString settings.port}/p2p/${peerID}"
            ) roles.bootstrap.machines;

            # Merge role-derived bootstrap nodes with manually specified extra nodes
            allBootstrapPeers = bootstrapPeersFromRole ++ settings.extraBootstrapPeers;
          in
          {
            assertions = [
              {
                assertion = allBootstrapPeers != [ ];
                message = "data-mesher: At least one bootstrap peer must be provided either via the 'bootstrap' role or 'extraBootstrapPeers'.";
              }
            ];

            clan.core.vars.generators =
              let
                # ensure generated secret files are readable by the data-mesher process
                # non secret files are going to be world-readable from the nix store
                mkSecretFile =
                  attrs:
                  attrs
                  // {
                    owner = dmConfig.user;
                    group = dmConfig.group;
                  };
              in
              {
                data-mesher-ca = {
                  share = true;
                  files = {
                    "ca.key".deploy = false;
                    "ca.pub".secret = false;
                  };
                  runtimeInputs = [
                    dmConfig.package
                  ];
                  script = ''
                    data-mesher generate ca --public-key-path "$out/ca.pub" --private-key-path "$out/ca.key"
                  '';
                };

                data-mesher-node-identity = {
                  dependencies = [
                    "data-mesher-ca"
                  ];
                  files = {
                    "peer.id".secret = false;
                    "identity.key" = mkSecretFile { };
                    "identity.pub".secret = false;
                    "identity.cert" = mkSecretFile { };
                  };
                  runtimeInputs = [
                    dmConfig.package
                  ];
                  script = ''
                    data-mesher generate identity-key \
                        --public-key-path "$out/identity.pub" \
                        --private-key-path "$out/identity.key"

                    data-mesher peer id "$out/identity.pub" > "$out/peer.id"

                    data-mesher certificate sign \
                        --ca-key "$in/data-mesher-ca/ca.key" \
                        --identity-key "$out/identity.pub" \
                        --output "$out/identity.cert" \
                        --validity 2160h    # 90 days for now TODO: expose this in the clan module
                  '';
                };
              };

            environment.systemPackages = [ dmConfig.package ];

            services.data-mesher = {
              enable = true;
              openFirewall = true;

              settings =
                let
                  gen = config.clan.core.vars.generators;
                in
                {
                  log_level = settings.logLevel;
                  cluster = {
                    port = settings.port;
                    interfaces = settings.interfaces;
                    bootstrap_peers = allBootstrapPeers;

                    push_pull_interval = "30s";

                    identity_key = gen.data-mesher-node-identity.files."identity.key".path;
                    identity_cert = gen.data-mesher-node-identity.files."identity.cert".path;
                    certificate_authorities = [ gen.data-mesher-ca.files."ca.pub".path ];
                  };

                  http.port = 7331;
                  http.interfaces = [ "lo" ]; # todo expose in options

                  files = mergedFiles;
                };
            };
          }
        );
      };
  };

  roles.bootstrap = {
    description = "A data-mesher bootstrap node that acts as an initial gateway when joining the cluster.";
    interface = { };
    perInstance =
      { ... }:
      {
        nixosModule = { ... }: { };
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
