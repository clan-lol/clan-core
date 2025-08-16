{
  lib,
  clanLib,
  config,
  options,
  ...
}:
let
  types = lib.types;

  metaOptionsWith = name: {
    name = lib.mkOption {
      type = types.str;
      default = name;
      description = ''
        Name of the machine or service
      '';
    };
    description = lib.mkOption {
      default = null;
      type = types.nullOr types.str;
      description = ''
        Optional freeform description
      '';
    };
    icon = lib.mkOption {
      default = null;
      type = types.nullOr types.str;
      description = ''
        Under construction, will be used for the UI
      '';
    };
  };
in
{
  imports = [
    (lib.mkRemovedOptionModule [ "services" ] ''
      The `inventory.services` option has been removed. Use `inventory.instances` instead.
      See: https://docs.clan.lol/concepts/inventory/#services
    '')
  ];
  options = {
    # Internal things
    _inventoryFile = lib.mkOption {
      type = types.path;
      readOnly = true;
      internal = true;
      visible = false;
    };
    noInstanceOptions = lib.mkOption {
      type = types.bool;
      internal = true;
      visible = false;
      default = false;
    };

    options = lib.mkOption {
      internal = true;
      visible = false;
      type = types.raw;
      default = options;
    };
    # ---------------------------

    modules = lib.mkOption {
      # Don't define the type yet
      # We manually transform the value with types.deferredModule.merge later to keep them serializable
      type = types.attrsOf types.raw;
      default = { };
      defaultText = "clanModules of clan-core";
      description = ''
        A mapping of module names to their path.

        Each module can be referenced by its `attributeName` in the `inventory.services` attribute set.

        !!! Important
            Each module MUST fulfill the following requirements to be usable with the inventory:

            - The module MUST have a `README.md` file with a `description`.
            - The module MUST have at least `features = [ "inventory" ]` in the frontmatter section.
            - The module MUST have a subfolder `roles` with at least one `{roleName}.nix` file.

            For further information see: [Module Authoring Guide](../../guides/authoring/clanServices/index.md).

        ???+ example
            ```nix
            clan-core.lib.clan {
                # 1. Add the module to the available inventory modules
                inventory.modules = {
                  custom-module = ./modules/my_module;
                };
                # 2. Use the module in the inventory
                inventory.services = {
                  custom-module.instance_1 = {
                      roles.default.machines = [ "machineA" ];
                  };
                };
            };
            ```
      '';

      apply = _: { };
    };

    assertions = lib.mkOption {
      type = types.listOf types.unspecified;
      internal = true;
      visible = false;
      default = [ ];
    };
    meta = lib.mkOption {
      type = lib.types.submoduleWith {
        modules = [
          ./meta-interface.nix
        ];
      };
    };
    tags = lib.mkOption {
      default = { };
      description = ''
        Tags of the inventory are used to group machines together.

        It is recommended to use [`machine.tags`](#inventory.machines.tags) to define the tags of the machines.

        This can be used to define custom tags that are either statically set or dynamically computed.

        #### Static Tags

        ???+ example "Static Tag Example"
            ```nix
            inventory.tags = {
              foo = [ "machineA" "machineB" ];
            };
            ```

            The tag `foo` will always be added to `machineA` and `machineB`.

        #### Dynamic Tags

        It is possible to compute tags based on the machines properties or based on other tags.

        !!! danger
            This is a powerful feature and should be used with caution.

            It is possible to cause infinite recursion by computing tags based on the machines properties or based on other tags.

        ???+ example "Dynamic Tag Example"

            allButFoo is a computed tag. It will be added to all machines except 'foo'

            `all` is a predefined tag. See the docs of [`tags.all`](#inventory.tags.all).

            ```nix
            #  inventory.tags ↓       ↓ inventory.machines
            inventory.tags = {config, machines...}: {
              #                                                        ↓↓↓ The "all" tag
              allButFoo = builtins.filter (name: name != "foo") config.all;
            };
            ```

        !!! warning
            Do NOT compute `tags` from `machine.tags` this will cause infinite recursion.
      '';
      type = types.submoduleWith {
        specialArgs = {
          inherit (config) machines;
        };
        modules = [
          {
            freeformType = with lib.types; lazyAttrsOf (listOf str);
            # Reserved tags
            # Defined as options here to show them in advance
            options = {
              # 'All machines' tag
              all = lib.mkOption {
                type = with lib.types; listOf str;
                defaultText = "[ <All Machines> ]";
                description = ''
                  !!! example "Predefined Tag"

                      Will be added to all machines

                      ```nix
                      inventory.machines.machineA.tags = [ "all" ];
                      ```
                '';
              };
              nixos = lib.mkOption {
                type = with lib.types; listOf str;
                defaultText = "[ <All NixOS Machines> ]";
                description = ''
                  !!! example "Predefined Tag"

                      Will be added to all machines that set `machineClass = "nixos"`

                      ```nix
                      inventory.machines.machineA.tags = [ "nixos" ];
                      ```
                '';
              };
              darwin = lib.mkOption {
                type = with lib.types; listOf str;
                defaultText = "[ <All Darwin Machines> ]";
                description = ''
                  !!! example "Predefined Tag"

                      Will be added to all machines that set `machineClass = "darwin"`

                      ```nix
                      inventory.machines.machineA.tags = [ "darwin" ];
                      ```
                '';
              };
            };
          }
        ];
      };
    };

    machines = lib.mkOption {
      description = ''
        Machines in the inventory.

        Each machine declared here can be referencd via its `attributeName` by the `inventory.service`s `roles`.
      '';
      default = { };
      type = types.lazyAttrsOf (
        types.submoduleWith ({
          modules = [
            (
              { name, ... }:
              {
                tags = builtins.attrNames (
                  # config.tags
                  lib.filterAttrs (_t: tagMembers: builtins.elem name tagMembers) config.tags
                );
              }
            )
            (
              { name, ... }:
              {
                options = {
                  inherit (metaOptionsWith name) name description icon;

                  machineClass = lib.mkOption {
                    default = "nixos";
                    type = types.enum [
                      "nixos"
                      "darwin"
                    ];
                    description = ''
                      The module system that should be used to construct the machine

                      Set this to `darwin` for macOS machines
                    '';
                  };

                  tags = lib.mkOption {
                    description = ''
                      List of tags for the machine.

                      The machine can be referenced by its tags in `inventory.services`

                      ???+ Example
                          ```nix
                          inventory.machines.machineA.tags = [ "tag1" "tag2" ];
                          ```

                          ```nix
                          services.borgbackup."instance_1".roles.client.tags = [ "tag1" ];
                          ```

                      !!! Note
                          Tags can be used to determine the membership of the machine in the services.
                          Without changing the service configuration, the machine can be added to a service by adding the correct tags to the machine.

                    '';
                    default = [ ];
                    apply = lib.unique;
                    type = types.listOf types.str;
                  };
                  deploy.targetHost = lib.mkOption {
                    description = "SSH address of the host to deploy the machine to";
                    default = null;
                    type = types.nullOr types.str;
                  };
                  deploy.buildHost = lib.mkOption {
                    description = "SSH address of the host to build the machine on";
                    default = null;
                    type = types.nullOr types.str;
                  };
                };
              }
            )
          ];
        })
      );
    };

    instances =
      if config.noInstanceOptions then
        { }
      else
        lib.mkOption {
          description = "Multi host service module instances";
          type = types.attrsOf (
            types.submoduleWith {
              modules = [
                (
                  { name, ... }:
                  {
                    options = {
                      # ModuleSpec
                      module = lib.mkOption {
                        default = { };
                        type = types.submodule {
                          options.input = lib.mkOption {
                            type = types.nullOr types.str;
                            default = null;
                            defaultText = "Name of the input. Default to 'null' which means the module is local";
                            description = ''
                              Name of the input. Default to 'null' which means the module is local
                            '';
                          };
                          options.name = lib.mkOption {
                            type = types.str;
                            default = name;
                            defaultText = "<Name of the Instance>";
                            description = ''
                              Attribute of the clan service module imported from the chosen input.

                              Defaults to the name of the instance.
                            '';
                          };
                        };
                      };
                      roles = lib.mkOption {
                        default = { };
                        type = types.attrsOf (
                          types.submodule {
                            imports = [
                              {
                                _file = "inventory/interface";
                                _module.args = {
                                  inherit clanLib;
                                };
                              }
                              (import ./roles-interface.nix { })
                            ];
                          }
                        );
                      };
                    };
                  }
                )
              ];
            }
          );
          default = { };
        };
  };
}
