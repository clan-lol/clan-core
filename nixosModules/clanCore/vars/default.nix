{
  _class,
  lib,
  config,
  pkgs,
  ...
}:
let
  inherit (lib.types) submoduleWith;
  submodule =
    module:
    submoduleWith {
      specialArgs.pkgs = pkgs;
      modules = [ module ];
    };
in
{
  imports =
    [
      ./public/in_repo.nix
      ./secret/fs.nix
      ./secret/sops
      ./secret/vm.nix
    ]
    ++ lib.optionals (_class == "nixos") [
      ./secret/password-store.nix
    ];
  options.clan.core.vars = lib.mkOption {
    description = ''
      Generated Variables

      Define generators that prompt for or generate variables like facts and secrets to store, deploy, and rotate them easily.
      For example, generators can be used to:
        - prompt the user for input, like passwords or host names
        - generate secrets like private keys automatically when they are needed
        - output multiple values like private and public keys simultaneously
    '';
    type = submodule { imports = [ ./interface.nix ]; };
  };

  config.system.clan.deployment.data = {
    vars = config.clan.core.vars._serialized;
    inherit (config.clan.core.networking) targetHost buildHost;
    inherit (config.clan.core.deployment) requireExplicitUpdate;
  };
}
