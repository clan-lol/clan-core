clan-core:
{
  config,
  lib,
  flake-parts-lib,
  inputs,
  self,
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
  imports = [
    # TODO: figure out how to print the deprecation warning
    # "${inputs.nixpkgs}/nixos/modules/misc/assertions.nix"
    (lib.mkRenamedOptionModule
      [
        "clan"
        "clanName"
      ]
      [
        "clan"
        "meta"
        "name"
      ]
    )
    (lib.mkRenamedOptionModule
      [
        "clan"
        "clanIcon"
      ]
      [
        "clan"
        "meta"
        "icon"
      ]
    )
  ];

  options.clan = {
    directory = mkOption {
      type = types.path;
      description = "The directory containing the clan subdirectory";
      default = self; # default to the directory of the flake
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

    # Checks are performed in 'buildClan'
    # Not everyone uses flake-parts
    meta = {
      name = lib.mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "Needs to be (globally) unique, as this determines the folder name where the flake gets downloaded to.";
      };
      icon = mkOption {
        type = types.nullOr types.path;
        default = null;
        description = "A path to an icon to be used for the clan in the GUI";
      };
      description = mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "A short description of the clan";
      };
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
          inventory = lib.mkOption { type = lib.types.attrsOf lib.types.unspecified; };
          meta = lib.mkOption { type = lib.types.attrsOf lib.types.unspecified; };
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
        pkgsForSystem
        meta
        ;
    };
  };
  _file = __curPos.file;
}
