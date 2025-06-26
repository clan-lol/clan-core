clan-core:
{
  config,
  lib,
  self,
  inputs,
  ...
}:
let
  inherit (lib) types;

  buildClanModule = clan-core.clanLib.buildClanModule;

in
{
  # Backwards compatibility
  imports = [
    (lib.mkRenamedOptionModule [ "clan" ] [ "flake" "clan" ])
  ];
  # Our module is completely public, so we dont need to map it
  # Mapped top level outputs
  options.flake = {
    # Backwards compat
    clanInternals = lib.mkOption {
      description = "Internals as used by the clan cli. Deprecated use clan.clanInternals";
      visible = false;
      readOnly = true;
      default = config.flake.clan.clanInternals;
      apply = lib.warn "Use clan.clanInternals instead";
    };
    # The one and only clan module
    clan = lib.mkOption {
      description = "The evaluated clan module";
      default = { };
      type = types.submoduleWith {
        specialArgs = {
          inherit clan-core self;
          inherit (inputs) nixpkgs nix-darwin;
          # TODO: inject the inventory interface
          # inventoryInterface = {};
        };
        modules = [
          buildClanModule.flakePartsModule
        ];
      };
    };

    # Mapped flake toplevel outputs
    darwinConfigurations = lib.mkOption {
      type = types.lazyAttrsOf types.raw;
      description = "darwinConfigurations produced by clan for a specific machine";
    };
    darwinModules = lib.mkOption {
      type = types.lazyAttrsOf types.deferredModule;
      description = "darwinModules produced by clan for a specific machine";
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
