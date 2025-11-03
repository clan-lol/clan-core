clan-core:
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
in
{
  # Backwards compatibility
  imports = [
    (lib.mkRenamedOptionModule [ "clan" ] [ "flake" "clan" ])
  ];
  options.flake = {
    # CLI compat
    clanInternals = lib.mkOption {
      description = "Stable nix interface interacted by the clan cli.";
      default = config.flake.clan.clanInternals;
    };
    # The clan module
    clan =
      # TODO: make these explizit options and deduplicate with lib.clan function
      let
        nixpkgs = inputs.nixpkgs or clan-core.inputs.nixpkgs;
        nix-darwin = inputs.nix-darwin or clan-core.inputs.nix-darwin;
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
            clan-core.modules.clan.default
          ];
        };
        # Important: !This logic needs to be kept in sync with lib.clan function!
        apply = config: clan-core.lib.checkConfig config.checks config;
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
