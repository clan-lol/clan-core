{
  config,
  lib,
  ...
}:
let
  cfg = config.clan.data-mesher;
  dmLib = import ./lib.nix lib;

  # the default bootstrap nodes are any machines with the admin or signers role
  # we iterate through those machines, determining an IP address for them based on their VPN
  # currently only supports zerotier
  defaultBootstrapNodes = builtins.foldl' (
    urls: name:
    let

      ipPath = "${config.clan.core.settings.directory}/vars/per-machine/${name}/zerotier/zerotier-ip/value";

    in
    if builtins.pathExists ipPath then
      let
        ip = builtins.readFile ipPath;
      in
      urls ++ [ "[${ip}]:${builtins.toString cfg.network.port}" ]
    else
      urls
  ) [ ] (dmLib.machines config).bootstrap;
in
{
  options.clan.data-mesher = {

    bootstrapNodes = lib.mkOption {
      type = lib.types.nullOr (lib.types.listOf lib.types.str);
      default = null;
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

  config = {

    services.data-mesher = {
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
          port = cfg.network.port;
          join_interval = "30s";
          push_pull_interval = "30s";

          interface = cfg.network.interface;

          bootstrap_nodes = if cfg.bootstrapNodes == null then defaultBootstrapNodes else cfg.bootstrapNodes;
        };

        http.port = 7331;
        http.interface = "lo";
      };
    };

    # Generate host key.
    clan.core.vars.generators.data-mesher-host-key = {
      files =
        let
          owner = config.users.users.data-mesher.name;
        in
        {
          private_key = {
            inherit owner;
          };
          public_key.secret = false;
        };

      runtimeInputs = [
        config.services.data-mesher.package
      ];

      script = ''
        data-mesher generate keypair \
            --public-key-path "$out"/public_key \
            --private-key-path "$out"/private_key
      '';
    };

    clan.core.vars.generators.data-mesher-network-key = {
      # generated once per clan
      share = true;

      files =
        let
          owner = config.users.users.data-mesher.name;
        in
        {
          private_key = {
            inherit owner;
          };
          public_key.secret = false;
        };

      runtimeInputs = [
        config.services.data-mesher.package
      ];

      script = ''
        data-mesher generate keypair \
            --public-key-path "$out"/public_key \
            --private-key-path "$out"/private_key
      '';
    };
  };
}
