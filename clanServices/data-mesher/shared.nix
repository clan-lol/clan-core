{
  config,
  settings,
  ...
}:
{

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
        port = settings.network.port;
        join_interval = "30s";
        push_pull_interval = "30s";
        interface = settings.network.interface;
        bootstrap_nodes = (builtins.attrValues settings.bootstrapNodes);
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
}
