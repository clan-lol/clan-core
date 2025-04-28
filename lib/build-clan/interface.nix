{
  lib,
  self,
  # TODO: Use dependency injection to allow for testing
  # inventoryInterface,
  ...
}:
let
  types = lib.types;
in
{
  options = {
    self = lib.mkOption {
      type = types.raw;
      default = self;
      defaultText = "Reference to the current flake";
      description = ''
        This is used to import external clan modules.
      '';
    };

    directory = lib.mkOption {
      type = types.coercedTo lib.types.raw (
        v:
        if lib.isAttrs v then
          lib.warn "It appears you set 'clan.directory = self'. Instead set 'clan.self = self'. 'clan.directory' expects a path" v
        else if v == null then
          throw "Please set either clan.self or clan.directory"
        else
          "${v}"
      ) lib.types.path;
      default = builtins.toString self;
      defaultText = "Root directory of the flake";
      description = ''
        The directory containing the clan.

        A typical directory structure could look like this:

        ```
        .
        ├── flake.nix
        ├── assets
        ├── machines
        ├── modules
        └── sops
        ```
      '';
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
      description = ''
        A mapping of machine names to their nixos configuration.

        ???+ example

            ```nix
            machines = {
              my-machine = {
                # Your nixos configuration
              };
            };
            ```
      '';
    };

    modules = lib.mkOption {
      type = types.attrsOf types.raw;
      default = { };
      description = ''
        An attribute set of exported modules.
      '';
    };

    templates = lib.mkOption {
      type = types.submodule { imports = [ ./templates/interface.nix ]; };
      default = { };
      description = ''
        Define Clan templates.
      '';
    };

    inventory = lib.mkOption {
      type = types.submodule { imports = [ ../inventory/build-inventory/interface.nix ]; };
      description = ''
        The `Inventory` submodule.

        For details see the [Inventory](./inventory.md) documentation.
      '';
    };

    # Meta
    meta = lib.mkOption {
      description = ''
        Global information about the clan.
      '';
      type = types.deferredModuleWith {
        staticModules = [ ../inventory/build-inventory/meta-interface.nix ];
      };
      default = { };
    };

    secrets = lib.mkOption {
      type = types.submodule { imports = [ ./secrets/interface.nix ]; };
      description = ''
        Secrets related options such as AGE plugins required to encrypt/decrypt secrets using the CLI.
      '';
      default = { };
    };

    pkgsForSystem = lib.mkOption {
      type = types.functionTo (types.nullOr types.attrs);
      default = _system: null;
      defaultText = "system: null";
      description = ''
        A function that maps from architecture to pkg. `( string -> pkgs )`

        If specified this nixpkgs will be only imported once for each system.
        This improves performance, but all `nixpkgs.*` options will be ignored.

        Returning `null` for a system will fallback to the default behavior of respecting the `nixpkgs.*` options.
      '';
    };

    # Outputs
    darwinConfigurations = lib.mkOption {
      # Hide from documentation.
      # Exposed at the top-level of the flake, clan.darwinConfigurations should not used by the user.
      # Instead, the user should use the `.#darwinConfigurations` attribute of the flake output.
      visible = false;
      type = types.lazyAttrsOf types.raw;
      default = { };
    };

    nixosConfigurations = lib.mkOption {
      # Hide from documentation.
      # Exposed at the top-level of the flake, clan.nixosConfigurations should not used by the user.
      # Instead, the user should use the `.#nixosConfigurations` attribute of the flake output.
      visible = false;
      type = types.lazyAttrsOf types.raw;
      default = { };
    };

    # flake.clanInternals
    clanInternals = lib.mkOption {
      # Hide from documentation. Exposes internals to the cli.
      visible = false;
      # ClanInternals
      type = types.submodule {
        freeformType = types.attrsOf types.raw;
        options = {
          # Those options are interfaced by the CLI
          # We don't specify the type here, for better performance.
          inventory = lib.mkOption { type = lib.types.raw; };
          inventoryValuesPrios = lib.mkOption { type = lib.types.raw; };
          # all exported clan templates from this clan
          templates = lib.mkOption { type = lib.types.raw; };
          # all exported clan modules from this clan
          modules = lib.mkOption { type = lib.types.raw; };
          # all inventory module schemas
          inventoryFile = lib.mkOption { type = lib.types.raw; };
          # The machine 'imports' generated by the inventory per machine
          inventoryClass = lib.mkOption { type = lib.types.raw; };
          # clan-core's modules
          clanModules = lib.mkOption { type = lib.types.raw; };
          source = lib.mkOption { type = lib.types.raw; };
          meta = lib.mkOption { type = lib.types.raw; };
          secrets = lib.mkOption { type = lib.types.raw; };
          clanLib = lib.mkOption { type = lib.types.raw; };
          all-machines-json = lib.mkOption { type = lib.types.raw; };
          machines = lib.mkOption { type = lib.types.raw; };
        };
      };
    };
  };
}
