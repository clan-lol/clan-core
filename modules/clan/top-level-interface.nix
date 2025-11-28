{
  lib,
  clanLib,
  self,
  config,
  # TODO: Use dependency injection to allow for testing
  # inventoryInterface,
  ...
}:
let
  types = lib.types;

  checkType = types.attrsOf (
    types.submodule {
      # Skip entire evaluation of this check
      options.ignore = lib.mkOption {
        type = types.bool;
        default = false;
        description = "Ignores this check entirely";
      };

      # Can only be defined once
      options.assertion = lib.mkOption {
        type = types.bool;
        readOnly = true;
        description = ''
          The assertion that must hold true.

          If false, the message is shown.
        '';
      };
      # Message shown when the assertion is false
      options.message = lib.mkOption {
        type = types.str;
        description = "Message shown when the assertion is false";
      };

      # TODO: add severity levels?
      # Fail, Warn, Log
    }
  );
in
{
  options = {
    _prefix = lib.mkOption {
      type = types.listOf types.str;
      internal = true;
      visible = false;
      default = [ ];
    };

    # internal options
    # dependency injection
    _dependencies.flake-config = lib.mkOption {
      type = types.raw;
      internal = true;
      default = null;
      description = ''
        The flake-parts-config if present
        'null' in case 'lib.clan' is used.
      '';
    };

    # id :: { assertion, message }
    checks = lib.mkOption {
      type = checkType;
      default = { };
      description = ''
        Assertions that must hold true when evaluating the clan.
        When the assertion fails, the message is shown and the evaluation is aborted.
      '';
    };

    self = lib.mkOption {
      type = types.raw;
      default = self;
      defaultText = "Reference to the current flake";
      description = ''
        This is used to import external clan modules.
      '';
      # Workaround for lib.clan
      apply =
        s:
        if lib.isAttrs s then
          s
          // {
            inputs = (s.inputs or { }) // {
              self.clan = config;
            };
          }
        else
          s;
    };

    directory = lib.mkOption {
      type = types.coercedTo lib.types.raw (
        v:
        if lib.isAttrs v then
          lib.warn "It appears you set 'clan.directory = self'. Instead set 'clan.self = self'. 'clan.directory' expects a path" v
        else if v == null then
          throw "Please set either clan.self or clan.directory"
        else
          v
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

    # TODO: make this writable by moving the options from inventoryClass into clan.
    exports = lib.mkOption {
      type = types.lazyAttrsOf (types.submoduleWith { modules = [ config.exportsModule ]; });
    };

    exportsModule = lib.mkOption {
      internal = true;
      visible = false;
      type = clanLib.types.exclusiveDeferredModule {
        warning = ''
          ! Non-standard exportsModule detected - clan incompatibility likely

          You've defined custom options in 'exportsModule' that aren't part of clan-core.
          Other clans won't be able to use your modules unless they define identical options.

          - Use central options from clan-core for compatibility
          - Developing new standards? Consider upstreaming
          - See: https://docs.clan.lol/reference/exports
        '';
      };
      description = ''
        A module that is used to define the module of flake level exports -

        such as 'exports.machines.<name>' and 'exports.instances.<name>'

        Example:

        ```nix
        {
          options.vars.generators = lib.mkOption {
            type = lib.types.attrsOf (
              lib.types.submoduleWith {
                modules = [
                  {
                    options.script = lib.mkOption { type = lib.types.str; };
                  }
                ];
              }
            );
            default = { };
          };
        }
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
      # Correct type would be `types.attrsOf types.deferredModule` but that allows for
      # Merging and transforms the value, which add eval overhead.
      type = types.attrsOf types.raw;
      default = { };
      description = ''
        An attribute set of exported modules.
      '';
    };

    templates = lib.mkOption {
      type = types.submodule { imports = [ ./templates.nix ]; };
      default = { };
      description = ''
        Define Clan templates.
      '';
    };

    inventory = lib.mkOption {
      type = types.submoduleWith {
        modules = [
          clanLib.inventory.inventoryModule
        ];
      };
      description = ''
        The `Inventory` submodule.

        For details see the [Inventory](/reference/options/clan_inventory.md) documentation.
      '';
    };

    # Meta
    meta = lib.mkOption {
      description = ''
        Global information about the clan.
      '';
      type = types.deferredModuleWith {
        staticModules = [ ../inventoryClass/meta.nix ];
      };
      default = { };
    };

    secrets = lib.mkOption {
      type = types.submodule { imports = [ ./secrets.nix ]; };
      description = ''
        Secrets related options such as AGE plugins required to encrypt/decrypt secrets using the CLI.
      '';
      default = { };
    };

    pkgsForSystem = lib.mkOption {
      type = types.functionTo (types.nullOr types.attrs);
      default =
        # If the user uses flake-parts default to use perSystem.clan.pkgs
        if config._dependencies.flake-config != null then
          (system: config._dependencies.flake-config.allSystems.${system}.clan.pkgs)
        else
          (_system: null);
      defaultText = "system: null";
      description = ''
        A function that maps from architecture to pkg. `( string -> pkgs )`

        Clan uses one global package set for all machines.
        Override this function to customize packages.

        When using flake-parts use 'perSystem.clan.pkgs' instead.

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

    nixosModules = lib.mkOption {
      # Hide from documentation.
      # Exposed at the top-level of the flake, clan.nixosModules should not used by the user.
      # Instead, the user should use the `.#nixosModules` attribute of the flake output.
      visible = false;
      type = types.lazyAttrsOf types.raw;
      default = { };
      description = ''
        NixOS modules that are generated by clan.
        These are used to generate the `nixosConfigurations`.
      '';
    };

    darwinModules = lib.mkOption {
      # Hide from documentation.
      # Exposed at the top-level of the flake, clan.darwinModules should not used by the user.
      # Instead, the user should use the `.#darwinModules` attribute of the flake output.
      visible = false;
      type = types.lazyAttrsOf types.raw;
      default = { };
      description = ''
        Darwin modules that are generated by clan.
        These are used to generate the `darwinConfigurations`.
      '';
    };

    # flake.clanInternals
    clanInternals = lib.mkOption {
      # Hide from documentation. Exposes internals to the cli.
      visible = false;
      # ClanInternals
      type = types.submodule {
        # Uncomment this if you want to add more stuff while debugging
        # freeformType = types.attrsOf types.raw;
        options = {
          # Those options are interfaced by the CLI
          # We don't specify the type here, for better performance.

          # The machine 'imports' generated by the inventory per machine
          inventoryClass = lib.mkOption {
            type = types.submoduleWith {
              modules = [ ];
            };
          };

          secrets = lib.mkOption { type = lib.types.raw; };

          templates = lib.mkOption { type = lib.types.raw; };

          machines = lib.mkOption { type = lib.types.raw; };
        };
      };
    };
  };

  config.exportsModule = {
    options.peer = lib.mkOption {
      default = null;
      type = lib.types.nullOr (
        lib.types.submodule (
          { name, ... }:
          {
            options = {
              name = lib.mkOption {
                type = lib.types.str;
                default = name;
              };
              SSHOptions = lib.mkOption {
                type = lib.types.listOf lib.types.str;
                default = [ ];
              };
              hosts = lib.mkOption {
                description = '''';
                type = lib.types.listOf (
                  lib.types.attrTag {
                    plain = lib.mkOption {
                      type = lib.types.str;
                      description = ''
                        a plain value, which can be read directly from the config
                      '';
                    };
                    var = lib.mkOption {
                      type = lib.types.submodule {
                        options = {
                          machine = lib.mkOption {
                            type = lib.types.str;
                            example = "jon";
                          };
                          generator = lib.mkOption {
                            type = lib.types.str;
                            example = "tor-ssh";
                          };
                          file = lib.mkOption {
                            type = lib.types.str;
                            example = "hostname";
                          };
                        };
                      };
                    };
                  }
                );
              };
            };
          }
        )
      );
    };

    options.networking = lib.mkOption {
      default = null;
      type = lib.types.nullOr (
        lib.types.submodule {
          options = {
            priority = lib.mkOption {
              type = lib.types.int;
              default = 1000;
              description = ''
                priority with which this network should be tried.
                higher priority means it gets used earlier in the chain
              '';
            };
            module = lib.mkOption {
              # type = lib.types.enum [
              #   "clan_lib.network.direct"
              #   "clan_lib.network.tor"
              # ];
              type = lib.types.str;
              default = "clan_lib.network.direct";
              description = ''
                the technology this network uses to connect to the target
                This is used for userspace networking with socks proxies.
              '';
            };
          };
        }
      );
    };
  };
}
