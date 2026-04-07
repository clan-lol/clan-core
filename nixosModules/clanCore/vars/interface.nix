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
          (
            generator:
            (lib.modules.importApply ../../../modules/clan/export-modules/generic-generator.nix {
              fileContextModule = {
                options.deploy = mkOption {
                  description = ''
                    Whether the file should be deployed to the target machine.

                    Disable this if the generated file is only used as an input to other generators.
                  '';
                  type = lib.types.bool;
                  default = true;
                };
                options.share = mkOption {
                  type = lib.types.bool;
                  description = ''
                    Whether the generated vars should be shared between machines.
                    Shared vars are only generated once, when the first machine using it is deployed.
                    Subsequent machines will re-use the already generated values.
                  '';
                  readOnly = true;
                  internal = true;
                  default = generator.config.share;
                  defaultText = "Mirror of the share flag of the generator";
                };
              };
            })
          )

          {
            options.dependencies = mkOption {
              description = ''
                A list of other generators that this generator depends on.
                The output values of these generators will be available to the generator script as files.

                For example:

                **A file `file1` of a generator named `dep1` will be available via `$in/dep1/file1`**
              '';
              type = lib.types.listOf lib.types.str;
              default = [ ];
            };
          }
          {
            inherit (config) pkgs settings;
          }
          # needed for mkRemovedOptionModule
          (config.pkgs.path + "/nixos/modules/misc/assertions.nix")
          (lib.mkRemovedOptionModule [ "migrateFact" ] ''
            The `migrateFact` option has been removed.
            The facts system has been fully removed from clan-core.
            See https://docs.clan.lol/guides/migrations/migration-facts-vars/ for manual migration instructions.
          '')
        ];
      });
    };
  };
}
