{ lib, ... }:
{
  options.clan.core.vars = lib.mkOption {
    internal = true;
    description = ''
      Generated Variables

      Define generators that prompt for or generate variables like facts and secrets to store, deploy, and rotate them easily.
      For example, generators can be used to:
        - prompt the user for input, like passwords or host names
        - generate secrets like private keys automatically when they are needed
        - output multiple values like private and public keys simultaneously
    '';
    type = lib.types.submoduleWith { modules = [ ./interface.nix ]; };
  };
}
