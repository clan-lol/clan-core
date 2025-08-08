{ ... }:
let
  sharedInterface =
    { lib, ... }:
    {
      options = {
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
        };
      };
    };

  mkBootstrapNodes =
    {
      config,
      lib,
      roles,
      settings,
    }:
    lib.mkDefault (
      builtins.foldl' (
        urls: name:
        let
          ipPath = "${config.clan.core.settings.directory}/vars/per-machine/${name}/zerotier/zerotier-ip/value";
        in
        if builtins.pathExists ipPath then
          let
            ip = builtins.readFile ipPath;
          in
          urls ++ [ "[${ip}]:${builtins.toString settings.network.port}" ]
        else
          urls
      ) [ ] (builtins.attrNames ((roles.admin.machines or { }) // (roles.signer.machines or { })))
    );

  mkDmService = dmSettings: config: {
    enable = true;
    openFirewall = true;

    settings = {
      log_level = "warn";
      state_dir = "/var/lib/data-mesher";

      # read network id from vars
      network.id = config.clan.core.vars.generators.data-mesher-network-key.files.public_key.value;

      host = {
        names = [ config.networking.hostName ];
        key_path = config.clan.core.vars.generators.data-mesher-host-key.files.private_key.path;
      };

      cluster = {
        port = dmSettings.network.port;
        join_interval = "30s";
        push_pull_interval = "30s";
        interface = dmSettings.network.interface;
        bootstrap_nodes = dmSettings.bootstrapNodes;
      };

      http.port = 7331;
      http.interface = "lo";
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
      {
        extendSettings,
        roles,
        lib,
        ...
      }:
      {
        nixosModule =
          { config, ... }:
          let
            settings = extendSettings {
              bootstrapNodes = mkBootstrapNodes {
                inherit
                  config
                  lib
                  roles
                  settings
                  ;
              };
            };
          in
          {
            imports = [ ./shared.nix ];

            services.data-mesher = (mkDmService settings config) // {
              initNetwork =
                let
                  # for a given machine, read it's public key and remove any new lines
                  readHostKey =
                    machine:
                    let
                      path = "${config.clan.core.settings.directory}/vars/per-machine/${machine}/data-mesher-host-key/public_key/value";
                    in
                    builtins.elemAt (lib.splitString "\n" (builtins.readFile path)) 1;
                in
                {
                  enable = true;
                  keyPath = config.clan.core.vars.generators.data-mesher-network-key.files.private_key.path;

                  tld = settings.network.tld;
                  hostTTL = settings.network.hostTTL;

                  # admin and signer host public keys
                  signingKeys = builtins.map readHostKey (
                    builtins.attrNames ((roles.admin.machines or { }) // (roles.signer.machines or { }))
                  );
                };
            };
          };
      };
  };

  roles.signer = {
    interface = sharedInterface;
    perInstance =
      {
        extendSettings,
        lib,
        roles,
        ...
      }:
      {
        nixosModule =
          { config, ... }:
          let
            settings = extendSettings {
              bootstrapNodes = mkBootstrapNodes {
                inherit
                  config
                  lib
                  roles
                  settings
                  ;
              };
            };
          in
          {
            imports = [ ./shared.nix ];
            services.data-mesher = (mkDmService settings config);
          };
      };
  };

  roles.peer = {
    interface = sharedInterface;
    perInstance =
      {
        extendSettings,
        lib,
        roles,
        ...
      }:
      {
        nixosModule =
          { config, ... }:
          let
            settings = extendSettings {
              bootstrapNodes = mkBootstrapNodes {
                inherit
                  config
                  lib
                  roles
                  settings
                  ;
              };
            };
          in
          {
            imports = [ ./shared.nix ];
            services.data-mesher = (mkDmService settings config);
          };
      };
  };
}
