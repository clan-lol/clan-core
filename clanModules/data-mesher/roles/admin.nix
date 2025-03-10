{ lib, config, ... }:
let
  cfg = config.clan.data-mesher;

  dmLib = import ../lib.nix lib;
in
{
  imports = [
    ../shared.nix
  ];

  options.clan.data-mesher = {
    network = {
      tld = lib.mkOption {
        type = lib.types.str;
        default = (config.networking.domain or "clan");
        description = "Top level domain to use for the network";
      };

      hostTTL = lib.mkOption {
        type = lib.types.str;
        default = "672h"; # 28 days
        example = "24h";
        description = "The TTL for hosts in the network, in the form of a Go time.Duration";
      };
    };
  };

  config = {
    services.data-mesher.initNetwork =
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

        tld = cfg.network.tld;
        hostTTL = cfg.network.hostTTL;

        # admin and signer host public keys
        signingKeys = builtins.map readHostKey (dmLib.machines config).bootstrap;
      };
  };
}
