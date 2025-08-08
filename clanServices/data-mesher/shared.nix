{
  config,
  ...
}:
{

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
