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

  publicAttrs = import ../lib/modules/public.nix;
  # Create output options only for listed attributes
  # TODO: Refactor this into an explicit module, so we can have description and other attributes to be listed in flake-parts
  outputModule = {
    clan = lib.genAttrs publicAttrs.clan (
      name: config.clan.${name} or (throw "Output: clan.${name} not found.")
    );
    topLevel = {
      options = lib.genAttrs publicAttrs.topLevel (_: lib.mkOption { });
      config = lib.genAttrs publicAttrs.topLevel (
        name: config.clan.${name} or (throw "Output: clan.${name} not found.")
      );
    };
  };
in
{
  options.clan = lib.mkOption {
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

  options.flake = {
    clan = lib.mkOption { type = types.raw; };
  } // outputModule.topLevel.options;

  config = {
    flake = {
      clan = outputModule.clan;
    } // outputModule.topLevel.config;
  };

  _file = __curPos.file;
}
