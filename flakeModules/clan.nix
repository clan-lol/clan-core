clan-core:
{
  config,
  lib,
  flake-parts-lib,
  self,
  inputs,
  ...
}:
let
  inherit (lib) types;

  buildClanModule = clan-core.clanLib.buildClanModule;

  publicAttrs = import ../lib/build-clan/public.nix;
  # Create output options only for listed attributes
  outputModule = {
    clan = lib.genAttrs publicAttrs.clan (
      name:
      config.clan.clanInternals.${name}
        or (throw "Output: clanInternals.${name} not found. Check: ${config.file}")
    );
    topLevel = {
      options = lib.genAttrs publicAttrs.topLevel (_: lib.mkOption { });
      config = lib.genAttrs publicAttrs.topLevel (
        name: config.clan.${name} or (throw "Output: clan.${name} not found. See: ${config.file}")
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

  options.flake =
    flake-parts-lib.mkSubmoduleOptions {
      clan = lib.mkOption { type = types.raw; };
    }
    // outputModule.topLevel.options;
  config = {
    flake = {
      clan = outputModule.clan;
    } // outputModule.topLevel.config;
  };

  _file = __curPos.file;
}
