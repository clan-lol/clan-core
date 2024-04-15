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
  buildClan = import ../lib/build-clan {
    inherit lib clan-core;
    inherit (inputs) nixpkgs;
  };

  cfg = config.clan;
in
{
  options.clan = {
    directory = mkOption {
      type = types.path;
      description = "The directory containing the clan subdirectory";
    };
    specialArgs = mkOption {
      type = types.attrsOf types.raw;
      default = { };
      description = "Extra arguments to pass to nixosSystem i.e. useful to make self available";
    };
    machines = mkOption {
      type = types.attrsOf types.raw;
      default = { };
      description = "Allows to include machine-specific modules i.e. machines.\${name} = { ... }";
    };
    clanName = mkOption {
      type = types.str;
      description = "Needs to be (globally) unique, as this determines the folder name where the flake gets downloaded to.";
    };
    clanIcon = mkOption {
      type = types.nullOr types.path;
      default = null;
      description = "A path to an icon to be used for the clan, should be the same for all machines";
    };
    pkgsForSystem = mkOption {
      type = types.functionTo types.raw;
      default = _system: null;
      description = "A map from arch to pkgs, if specified this nixpkgs will be only imported once for each system.";
    };
  };
  options.flake = flake-parts-lib.mkSubmoduleOptions {
    clanInternals = lib.mkOption {
      type = lib.types.submodule {
        options = {
          all-machines-json = lib.mkOption { type = lib.types.attrsOf lib.types.unspecified; };
          machines = lib.mkOption { type = lib.types.attrsOf (lib.types.attrsOf lib.types.unspecified); };
          machinesFunc = lib.mkOption { type = lib.types.attrsOf (lib.types.attrsOf lib.types.unspecified); };
        };
      };
    };
  };
  config = {
    flake = buildClan {
      inherit (cfg)
        directory
        specialArgs
        machines
        clanName
        clanIcon
        pkgsForSystem
        ;
    };
  };
  _file = __curPos.file;
}
