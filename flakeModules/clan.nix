# Attention!
# Don't add 'clan-core' to this list.
# Instead explicitly forward the attribute for transparency and explizitness.
{
  flake-parts-lib,
  coreModules,
  coreInputs,
  clanLib,
}:
# Downstream flake arguments
{
  self,
  inputs,
  config,
  lib,
  ...
}:
let
  inherit (lib) types;

  inherit (flake-parts-lib)
    mkPerSystemOption
    ;

in
{
  # Backwards compatibility
  imports = [
    (lib.mkRenamedOptionModule [ "clan" ] [ "flake" "clan" ])
  ];

  options.perSystem = mkPerSystemOption {
    options.clan.pkgs = lib.mkOption {
      description = ''
        Packages for system

        This will set the pkgs for every system used in a 'clan'

        !!! Warning
            If pkgsForSystem is set explicitly, that has higher precedence.

            This option has no effect if pkgsForSystem is set.
      '';
      type = types.raw;
      default = null;
    };
  };

  options.flake = {
    # CLI compat
    clanInternals = lib.mkOption {
      description = "Stable nix interface interacted by the clan cli.";
      default = config.flake.clan.clanInternals;
    };
    # The clan module
    clan =
      # TODO: make these explicit options and deduplicate with lib.clan function
      let
        nixpkgs = inputs.nixpkgs or coreInputs.nixpkgs;
        nix-darwin = inputs.nix-darwin or coreInputs.nix-darwin;
      in
      lib.mkOption {
        description = "Clan module. Define your clan inside here";
        default = { };
        type = types.submoduleWith {
          class = "clan";
          specialArgs = {
            inherit self;
            inherit nixpkgs nix-darwin;
          };
          modules = [
            coreModules.clan.default

            # Inject the users flake-config from flake-parts
            { _dependencies.flake-config = config; }
          ];
        };
        # Important: !This logic needs to be kept in sync with lib.clan function!
        apply = config: clanLib.checkConfig config.checks config;
      };

    # Mapped flake toplevel outputs
    darwinConfigurations = lib.mkOption {
      type = types.lazyAttrsOf types.raw;
      description = "darwinConfigurations produced by clan for a specific machine";
    };
    darwinModules = lib.mkOption {
      type = types.lazyAttrsOf types.deferredModule;
      description = "darwinModules produced by clan for a specific machine";
      apply = lib.mapAttrs (
        k: v: {
          _file = "#darwinModules.${k}";
          imports = [ v ];
        }
      );
    };
  };
  # Use normal prio, to allow merging with user values
  config.flake = {
    inherit (config.flake.clan)
      nixosConfigurations
      nixosModules
      darwinConfigurations
      darwinModules
      ;
  };

  _file = __curPos.file;
}
