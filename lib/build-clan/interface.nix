{ lib, ... }:
let
  types = lib.types;
in
{
  options = {
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
    pkgsForSystem = lib.mkOption {
      type = types.functionTo (types.nullOr types.attrs);
      default = _: null;
    };
    inventory = lib.mkOption {
      type = types.submodule { imports = [ ../inventory/build-inventory/interface.nix ]; };
    };

    # Outputs
    # flake.clanInternals
    clanInternals = lib.mkOption {
      type = types.submodule {
        options = {
          # Those options are interfaced by the CLI
          inventory = lib.mkOption { type = lib.types.attrsOf lib.types.unspecified; };
          inventoryFile = lib.mkOption { type = lib.types.unspecified; };
          clanModules = lib.mkOption { type = lib.types.attrsOf lib.types.path; };
          source = lib.mkOption { type = lib.types.path; };
          meta = lib.mkOption { type = lib.types.attrsOf lib.types.unspecified; };
          all-machines-json = lib.mkOption { type = lib.types.attrsOf lib.types.unspecified; };
          machines = lib.mkOption { type = lib.types.attrsOf (lib.types.attrsOf lib.types.unspecified); };
          machinesFunc = lib.mkOption { type = lib.types.attrsOf (lib.types.attrsOf lib.types.unspecified); };
        };
      };
    };
  };
}
