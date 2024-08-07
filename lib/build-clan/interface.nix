{ lib, ... }:
let
  types = lib.types;
in
{
  options = {
    # Required options
    directory = lib.mkOption {
      type = types.path;
      description = "The directory containing the clan subdirectory";
    };

    specialArgs = lib.mkOption {
      type = types.attrsOf types.raw;
      default = { };
      description = "Extra arguments to pass to nixosSystem i.e. useful to make self available";
    };

    # Optional
    machines = lib.mkOption {
      type = types.attrsOf types.deferredModule;
      default = { };
    };
    inventory = lib.mkOption {
      type = types.submodule { imports = [ ../inventory/build-inventory/interface.nix ]; };
    };

    # Meta
    meta = {
      name = lib.mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "Needs to be (globally) unique, as this determines the folder name where the flake gets downloaded to.";
      };
      icon = lib.mkOption {
        type = types.nullOr types.path;
        default = null;
        description = "A path to an icon to be used for the clan in the GUI";
      };
      description = lib.mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "A short description of the clan";
      };
    };

    pkgsForSystem = lib.mkOption {
      type = types.functionTo (types.nullOr types.attrs);
      default = _: null;
    };

    # Outputs
    nixosConfigurations = lib.mkOption {
      type = types.lazyAttrsOf types.raw;
      default = { };
    };
    # flake.clanInternals
    clanInternals = lib.mkOption {
      # type = types.raw;
      # ClanInternals
      type = types.submodule {
        options = {
          # Those options are interfaced by the CLI
          # We don't speficy the type here, for better performance.
          inventory = lib.mkOption { type = lib.types.raw; };
          inventoryFile = lib.mkOption { type = lib.types.raw; };
          clanModules = lib.mkOption { type = lib.types.raw; };
          source = lib.mkOption { type = lib.types.raw; };
          meta = lib.mkOption { type = lib.types.raw; };
          all-machines-json = lib.mkOption { type = lib.types.raw; };
          machines = lib.mkOption { type = lib.types.raw; };
          machinesFunc = lib.mkOption { type = lib.types.raw; };
        };
      };
    };
  };
}
