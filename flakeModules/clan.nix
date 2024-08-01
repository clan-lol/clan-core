clan-core:
{
  config,
  lib,
  flake-parts-lib,
  inputs,
  ...
}:
let
  inherit (lib) mkOption types;
in
{

  options.clan = lib.mkOption {
    type = types.submoduleWith {
      # _module.args = {
      # };
      specialArgs = {
        inherit clan-core;
        inherit (inputs) nixpkgs;
      };
      modules = [
        ../lib/build-clan/interface.nix
        ../lib/build-clan/module.nix
      ];
    };
  };

  options.flake = flake-parts-lib.mkSubmoduleOptions {
    clanInternals = lib.mkOption { type = types.raw; };
  };
  config = {
    flake.clanInternals = config.clan.clanInternals;
    flake.nixosConfigurations = config.clan.nixosConfigurations;
  };
  _file = __curPos.file;
}
