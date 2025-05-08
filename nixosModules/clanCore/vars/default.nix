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
      class = _class;
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

  config = {
    # check all that all non-secret files have no owner/group/mode set
    warnings = lib.foldl' (
      warnings: generator:
      warnings
      ++ lib.foldl' (
        warnings: file:
        warnings
        ++
          lib.optional
            (
              !file.secret
              && (
                file.owner != "root"
                || file.group != (if _class == "darwin" then "wheel" else "root")
                || file.mode != "0400"
              )
            )
            ''
              The config.clan.core.vars.generators.${generator.name}.files.${file.name} is not secret:
              ${lib.optionalString (file.owner != "root") ''
                The owner is set to ${file.owner}, but should be root.
              ''}
              ${lib.optionalString (file.group != (if _class == "darwin" then "wheel" else "root")) ''
                The group is set to ${file.group}, but should be ${if _class == "darwin" then "wheel" else "root"}.
              ''}
              ${lib.optionalString (file.mode != "0400") ''
                The mode is set to ${file.mode}, but should be 0400.
              ''}
              This doesn't work because the file will be added to the nix store
            ''
      ) [ ] (lib.attrValues generator.files)
    ) [ ] (lib.attrValues config.clan.core.vars.generators);

    system.clan.deployment.data = {
      vars = config.clan.core.vars._serialized;
      inherit (config.clan.core.networking) targetHost buildHost;
      inherit (config.clan.core.deployment) requireExplicitUpdate;
    };
  };
}
