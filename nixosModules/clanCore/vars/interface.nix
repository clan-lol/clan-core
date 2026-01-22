{
  lib,
  config,
  ...
}:
let
  inherit (lib)
    mkOption
    ;
  inherit (lib.types)
    attrsOf
    raw
    submodule
    submoduleWith
    ;
in
{
  options = {
    # ===
    # Injected dependencies
    # ===
    globalSettings = mkOption {
      description = ''
        The global vars settings for the whole clan.

        This is a deferred module that is merged with the local settings of this machine
      '';
      type = lib.types.deferredModuleWith {
        staticModules = [ ../../../modules/clan/vars/settings-opts.nix ];
      };
      internal = true;
      visible = false;
      default = { };
    };
    pkgs = mkOption {
      description = ''
        The pkgs set to use for vars generators.
        This is usually inherited from the nixos pkgs set.
      '';
      type = raw;
      internal = true;
    };
    # ===
    # Global vars settings
    # ===
    settings = mkOption {
      description = ''
        Settings for the vars module.
      '';
      type = submodule config.globalSettings;
      default = { };
    };

    # ===
    # Generators
    # ===
    generators = mkOption {
      description = ''
        A set of generators that can be used to generate files.
        Generators are scripts that produce files based on the values of other generators and user input.
        Each generator is expected to produce a set of files under a directory.
      '';
      default = { };
      type = attrsOf (submoduleWith {
        modules = [
          {
            imports = [
              # Inject dependencies from the 'nixos' module
              {
                inherit (config) pkgs settings;
              }
              ../../../modules/clan/export-modules/generator.nix
              # needed for mkRemovedOptionModule
              (config.pkgs.path + "/nixos/modules/misc/assertions.nix")
              (lib.mkRemovedOptionModule [ "migrateFact" ] ''
                The `migrateFact` option has been removed.
                The facts system has been fully removed from clan-core.
                See https://docs.clan.lol/guides/migrations/migration-facts-vars/ for manual migration instructions.
              '')
            ];
          }
        ];
      });
    };
  };
}
