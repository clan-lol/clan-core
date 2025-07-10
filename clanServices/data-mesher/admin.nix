{
  lib,
  config,
  settings,
  ...
}:
{

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

      tld = settings.network.tld;
      hostTTL = settings.network.hostTTL;

      # admin and signer host public keys
      signingKeys = builtins.map readHostKey (builtins.attrNames settings.bootstrapNodes);
    };
}
