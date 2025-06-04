{ lib, config, ... }:
let
  inherit (lib) mkOption types;
  inherit (types) attrsWith submoduleWith;

  # TODO:
  # Remove once this gets merged upstream; performs in O(n*log(n) instead of O(n^2))
  # https://github.com/NixOS/nixpkgs/pull/355616/files
  uniqueStrings = list: builtins.attrNames (builtins.groupBy lib.id list);

  checkInstanceRoles =
    instanceName: instanceRoles:
    let
      unmatchedRoles = lib.filter (roleName: !lib.elem roleName (lib.attrNames config.roles)) (
        lib.attrNames instanceRoles
      );
    in
    if unmatchedRoles == [ ] then
      true
    else
      throw ''
        inventory instance: 'instances.${instanceName}' defines the following roles:
        ${builtins.toJSON unmatchedRoles}

        But the clan-service module '${config.manifest.name}' defines roles:
        ${builtins.toJSON (lib.attrNames config.roles)}
      '';

  /**
    Merges the role- and machine-settings using the role interface

    Arguments:

    - roleName: The name of the role
    - instanceName: The name of the instance
    - settings: The settings of the machine. Leave empty to get the role settings

    Returns: evalModules result

    The caller is responsible to use .config or .extendModules
  */
  # TODO: evaluate against the role.settings statically and use extendModules to get the machineSettings
  # Doing this might improve performance
  evalMachineSettings =
    {
      roleName,
      instanceName,
      machineName ? null,
      settings,
    }:
    lib.evalModules {
      # Prefix for better error reporting
      # This prints the path where the option should be defined rather than the plain path within settings
      # "The option `instances.foo.roles.server.machines.test.settings.<>' was accessed but has no value defined. Try setting the option."
      prefix =
        [
          "instances"
          instanceName
          "roles"
          roleName
        ]
        ++ (lib.optionals (machineName != null) [
          "machines"
          machineName
        ])
        ++ [ "settings" ];

      # This may lead to better error reporting
      # And catch errors if anyone tried to import i.e. a nixosConfiguration
      # Set some class: i.e "network.server.settings"
      class = lib.concatStringsSep "." [
        config.manifest.name
        roleName
        "settings"
      ];

      modules = [
        (lib.setDefaultModuleLocation "Via clan.service module: roles.${roleName}.interface"
          config.roles.${roleName}.interface
        )
        (lib.setDefaultModuleLocation "inventory.instances.${instanceName}.roles.${roleName}.settings"
          config.instances.${instanceName}.roles.${roleName}.settings
        )
        settings
        # Dont set the module location here
        # This should already be set by the tags resolver
        # config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.settings
      ];
    };

  /**
    Makes a module extensible
    returning its config
    and making it extensible via '__functor' polymorphism

    Example:

    ```nix-repl
    res = makeExtensibleConfig (evalModules { options.foo = mkOption { default = 42; };)
    res
    =>
    {
      foo = 42;
      _functor = <function>;
    }

    # This allows to override using mkDefault, mkForce, etc.
    res { foo = 100; }
    =>
    {
      foo = 100;
      _functor = <function>;
    }
    ```
  */

  # Extend evalModules result by a module, returns .config.
  extendEval = eval: m: (eval.extendModules { modules = lib.toList m; }).config;

  /**
    Apply the settings to the instance

    Takes a [ServiceInstance] :: { roles :: { roleName :: { machines :: { machineName :: { settings :: { ... } } } } } }
    Returns the same object but evaluates the settings against the interface.

    We need this because 'perMachine' shouldn't gain access the raw deferred module.
  */
  applySettings =
    instanceName: instance:
    lib.mapAttrs (roleName: role: {
      machines = lib.mapAttrs (machineName: v: {
        # TODO: evaluate the settings against the interface
        # settings = (evalMachineSettings { inherit roleName instanceName; inherit (v) settings; }).config;
        settings =
          (evalMachineSettings {
            inherit roleName instanceName machineName;
            inherit (v) settings;
          }).config;
      }) role.machines;
      # TODO: evaluate the settings against the interface
      settings =
        (evalMachineSettings {
          inherit roleName instanceName;
          inherit (role) settings;
        }).config;
    }) instance.roles;
in
{
  options = {
    # TODO: deduplicate this with inventory.instances
    # Although inventory has stricter constraints
    instances = mkOption {
      # Instances are created in the inventory
      visible = false;
      defaultText = "Throws: 'The service must define its instances' when not defined";
      default = throw ''
        The clan service module ${config.manifest.name} doesn't define any instances.

        Did you forget to create instances via 'inventory.instances'?
      '';
      description = ''
        Instances of the service.

        An Instance is a user-specific deployment or configuration of a service.
        It represents the active usage of the service configured to the user's settings or use case.
        The `<instanceName>` of the instance is arbitrary, but must be unique.

        A common best practice is to name the instance after the 'service' and the 'use-case'.

        For example:

        - 'instances.zerotier-homelab = ...' for a zerotier instance that connects all machines of a homelab
      '';

      type = attrsWith {
        placeholder = "instanceName";
        elemType = submoduleWith {
          modules = [
            (
              { name, ... }:
              {
                # options.settings = mkOption {
                #   description = "settings of 'instance': ${name}";
                #   default = {};
                #   apply = v: lib.seq (checkInstanceSettings name v) v;
                # };
                options.roles = mkOption {
                  description = ''
                    Roles of the instance.

                    A role is a specific behavior or configuration of the service.
                    It defines how the service should behave in the context of this instance.
                    The `<roleName>` must match one of the roles defined in the service

                    For example:

                    - 'roles.client = ...' for a client role that connects to the service
                    - 'roles.server = ...' for a server role that provides the service

                    Throws an error if empty, since this would mean that the service has no members.
                  '';
                  defaultText = "Throws: 'The service must define members via roles' when not defined";
                  default = throw ''
                    Instance '${name}' of service '${config.manifest.name}' mut define members via 'roles'.

                    To include a machine:
                    'instances.${name}.roles.<role-name>.machines.<your-machine-name>' must be set.
                  '';
                  type = attrsWith {
                    placeholder = "roleName";
                    elemType = submoduleWith {
                      modules = [
                        ({
                          # instances.{instanceName}.roles.{roleName}.machines
                          options.machines = mkOption {
                            description = ''
                              Machines of the role.

                              A machine is a physical or virtual machine that is part of the instance.
                              The `<machineName>` must match the name of any machine defined in the clan.

                              For example:

                              - 'machines.my-machine = { ...; }' for a machine that is part of the instance
                              - 'machines.my-other-machine = { ...; }' for another machine that is part of the instance
                            '';
                            type = attrsWith {
                              placeholder = "machineName";
                              elemType = submoduleWith {
                                modules = [
                                  (m: {
                                    options.settings = mkOption {
                                      type = types.raw;
                                      description = "Settings of '${name}-machine': ${m.name or "<machineName>"}.";
                                      default = { };
                                    };
                                  })
                                ];
                              };
                            };
                          };

                            # instances.{instanceName}.roles.{roleName}.settings
                            # options._settings = mkOption { };
                            # options._settingsViaTags = mkOption { };
                            # A deferred module that combines _settingsViaTags with _settings
                            options.settings = mkOption {
                              type = types.raw;
                              description = "Settings of 'role': ${name}";
                              default = { };
                            };

                            options.extraModules = lib.mkOption {
                              default = [ ];
                              type = types.listOf (types.deferredModule);
                            };
                          }
                        )
                      ];
                    };
                  };
                  apply = v: lib.seq (checkInstanceRoles name v) v;
                };
              }
            )
          ];
        };
      };
    };

    manifest = mkOption {
      description = "Meta information about this module itself";
      type = submoduleWith {
        modules = [
          ./manifest/default.nix
        ];
      };
    };
    roles = mkOption {
      description = ''
        Roles of the service.

        A role is a specific behavior or configuration of the service.
        It defines how the service should behave in the context of the clan.

        The `<roleName>`s of the service are defined here. Later usage of the roles must match one of the `roleNames`.

        For example:

        - 'roles.client = ...' for a client role that connects to the service
        - 'roles.server = ...' for a server role that provides the service

        Throws an error if empty, since this would mean that the service has no way of adding members.
      '';
      defaultText = "Throws: 'The service must define its roles' when not defined";
      default = throw ''
        Role behavior of service '${config.manifest.name}' must be defined.
        A 'clan.service' module should always define its behavior via 'roles'
        ---
        To add the role:
        `roles.client = {}`

        To define multiple instance behavior:
        `roles.client.perInstance = { ... }: {}`
      '';
      type = attrsWith {
        placeholder = "roleName";
        elemType = submoduleWith {
          modules = [
            (
              { name, ... }:
              let
                roleName = name;
              in
              {
                options.interface = mkOption {
                  description = ''
                    Abstract interface of the role.

                    This is an abstract module which should define 'options' for the role's settings.

                    Example:

                    ```nix
                    {
                      options.timeout = mkOption {
                        type = types.int;
                        default = 30;
                        description = "Timeout in seconds";
                      };
                    }
                    ```

                    Note:

                    - `machine.config` is not available here, since the role is definition is abstract.
                    - *defaults* that depend on the *machine* or *instance* should be added to *settings* later in 'perInstance' or 'perMachine'
                  '';
                  type = types.deferredModule;
                  # TODO: Default to an empty module
                  # need to test that an the empty module can be evaluated to empty settings
                  default = { };
                };
                options.perInstance = mkOption {
                  description = ''
                    Per-instance configuration of the role.

                    This option is used to define instance-specific behavior for the service-role. (Example below)

                    Although the type is a `deferredModule`, it helps to think of it as a function.
                    The 'function' takes the `instance-name` and some other `arguments`.

                    *Arguments*:

                    - `instanceName` (`string`): The name of the instance.
                    - `machine`: Machine information, containing:
                      ```nix
                        {
                          name = "machineName";
                          roles = ["client" "server" ... ];
                        }
                      ```
                    - `roles`: Attribute set of all roles of the instance, in the form:
                      ```nix
                      roles = {
                        client = {
                          machines = {
                            jon = {
                              settings = {
                                timeout = 60;
                              };
                            };
                            # ...
                          };
                          settings = {
                            timeout = 30;
                          };
                        };
                        # ...
                      };
                      ```

                    - `settings`: The settings of the role, as defined in `inventory`
                      ```nix
                      {
                        timeout = 30;
                      }
                      ```
                    - `extendSettings`: A function that takes a module and returns a new module with extended settings.
                      ```nix
                      extendSettings {
                        timeout = mkForce 60;
                      };
                      ->
                      {
                        timeout = 60;
                      }
                      ```

                    *Returns* an `attribute set` containing:

                    - `nixosModule`: The NixOS module for the instance.

                  '';
                  type = types.deferredModuleWith {
                    staticModules = [
                      ({
                        options.nixosModule = mkOption {
                          type = types.deferredModule;
                          default = { };
                          description = ''
                            This module is later imported to configure the machine with the config derived from service's settings.

                            Example:

                            ```nix
                            roles.client.perInstance = { instanceName, ... }:
                            {
                              # Keep in mind that this module is produced once per-instance
                              # Meaning you might end up with multiple of these modules.
                              # Make sure they can be imported all together without conflicts
                              #
                              #                 ↓ nixos-config
                              nixosModule = { config ,... }: {
                                # create one systemd service per instance
                                # It is a common practice to concatenate the *service-name* and *instance-name*
                                # To ensure globally unique systemd-units for the target machine
                                systemd.services."webly-''${instanceName}" = {
                                  ...
                                };
                              };
                            }
                            ```
                          '';
                        };
                        # TODO: Recursive services
                        options.services = mkOption {
                          visible = false;
                          type = attrsWith {
                            placeholder = "serviceName";
                            elemType = submoduleWith {
                              modules = [ ./service-module.nix ];
                            };
                          };
                          apply = _: throw "Not implemented yet";
                          default = { };
                        };
                      })
                    ];
                  };
                  default = { };
                  apply =
                    /**
                      This apply transforms the module into a function that takes arguments and returns an evaluated module
                      The arguments of the function are determined by its scope:
                      -> 'perInstance' maps over all instances and over all machines hence it takes 'instanceName' and 'machineName' as iterator arguments
                    */
                    v: instanceName: machineName:
                    (lib.evalModules {
                      specialArgs =
                        let
                          roles = applySettings instanceName config.instances.${instanceName};
                        in
                        {
                          inherit instanceName roles;
                          machine = {
                            name = machineName;
                            roles = lib.attrNames (lib.filterAttrs (_n: v: v.machines ? ${machineName}) roles);
                          };
                          settings =
                            (evalMachineSettings {
                              inherit roleName instanceName machineName;
                              settings =
                                config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.settings or { };
                            }).config;
                          extendSettings = extendEval (evalMachineSettings {
                            inherit roleName instanceName machineName;
                            settings =
                              config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.settings or { };
                          });
                        };
                      modules = [ v ];
                    }).config;
                };
              }
            )
          ];
        };
      };
    };

    perMachine = mkOption {
      description = ''
        Per-machine configuration of the service.

        This option is used to define machine-specific settings for the service **once**, if any service-instance is used.

        Although the type is a `deferredModule`, it helps to think of it as a function.
        The 'function' takes the `machine-name` and some other 'arguments'

        *Arguments*:

        - `machine`: `{ name :: string; roles :: listOf String }`
        - `instances`: The scope of the machine, containing all instances and roles that the machine is part of.
          ```nix
          {
            instances = {
              <instanceName> = {
                roles = {
                  <roleName> = {
                    # Per-machine settings
                    machines = { <machineName> = { settings = { ... }; }; }; };
                    # Per-role settings
                    settings = { ... };
                };
              };
            };
          }
          ```

        *Returns* an `attribute set` containing:

        - `nixosModule`: The NixOS module for the machine.

      '';
      type = types.deferredModuleWith {
        staticModules = [
          ({
            options.nixosModule = mkOption {
              type = types.deferredModule;
              default = { };
              description = ''
                A single NixOS module for the machine.

                This module is later imported to configure the machine with the config derived from service's settings.

                Example:

                ```nix
                #              ↓ machine.roles ...
                perMachine = { machine, ... }:
                {               # ↓ nixos-config
                  nixosModule = { config ,... }: {
                    systemd.services.foo = {
                      enable = true;
                    };
                  }
                }
                ```
              '';
            };
            # TODO: Recursive services
            options.services = mkOption {
              visible = false;
              type = attrsWith {
                placeholder = "serviceName";
                elemType = submoduleWith {
                  modules = [ ./service-module.nix ];
                };
              };
              apply = _: throw "Not implemented yet";
              default = { };
            };
          })
        ];
      };
      default = { };
      apply =
        v: machineName: machineScope:
        (lib.evalModules {
          specialArgs = {
            /**
              This apply transforms the module into a function that takes arguments and returns an evaluated module
              The arguments of the function are determined by its scope:
              -> 'perMachine' maps over all machines of a service 'machineName' and a helper 'scope' (some aggregated attributes) as iterator arguments
              The 'scope' attribute is used to collect the 'roles' of all 'instances' where the machine is part of and inject both into the specialArgs
            */
            machine = {
              name = machineName;
              roles =
                let
                  collectRoles =
                    instances:
                    lib.foldlAttrs (
                      r: _instanceName: instance:
                      r
                      ++ lib.foldlAttrs (
                        r2: roleName: _role:
                        r2 ++ [ roleName ]
                      ) [ ] instance.roles
                    ) [ ] instances;
                in
                uniqueStrings (collectRoles machineScope.instances);
            };
            # TODO: instances.<instanceName>.roles should contain all roles, even if nobody has the role
            inherit (machineScope) instances;

            # There are no machine settings.
            # Settings are always role specific, having settings that apply to a machine globally would mean to merge all role and all instance settings into a single module.
            # But that will likely cause conflicts because it is inherently wrong.
            settings = throw ''
              'perMachine' doesn't have a 'settings' argument.

              Alternatives:
              - 'instances.<instanceName>.roles.<roleName>.settings' should be used instead.
              - 'instances.<instanceName>.roles.<roleName>.machines.<machineName>.settings' should be used instead.

              If that is insufficient, you might also consider using 'roles.<roleName>.perInstance' instead of 'perMachine'.
            '';
          };

          modules = [ v ];
        }).config;
    };
    # ---
    # Place the result in _module.result to mark them as "internal" and discourage usage/overrides
    #
    # ---
    # Intermediate result by mapping over the 'roles', 'instances', and 'machines'.
    # During this step the 'perMachine' and 'perInstance' are applied.
    # The result-set for a single machine can then be found by collecting all 'nixosModules' recursively.

    /**
      allRoles :: {
        <roleName> :: {
          allInstances :: {
            <instanceName> :: {
              allMachines :: {
                <machineName> :: {
                  nixosModule :: NixOSModule;
                  services :: { }; # TODO: nested services
                };
              };
            };
          };
        };
      }
    */
    result.allRoles = mkOption {
      visible = false;
      readOnly = true;
      default = lib.mapAttrs (roleName: roleCfg: {
        allInstances = lib.mapAttrs (instanceName: instanceCfg: {
          allMachines = lib.mapAttrs (
            machineName: _machineCfg:
            let
              instanceRes = roleCfg.perInstance instanceName machineName;
            in
            {
              nixosModule = {
                imports = [
                  # Result of the applied 'perInstance = {...}: {  nixosModule = { ... }; }'
                  instanceRes.nixosModule
                ] ++ instanceCfg.roles.${roleName}.extraModules;
              };
              # TODO: nested services
              services = { };
            }

          ) instanceCfg.roles.${roleName}.machines or { };
        }) config.instances;
      }) config.roles;
    };

    result.assertions = mkOption {
      default = { };
      visible = false;
      type = types.attrsOf types.raw;
    };

    result.allMachines = mkOption {
      visible = false;
      readOnly = true;
      default =
        let
          collectMachinesFromInstance =
            instance:
            uniqueStrings (
              lib.foldlAttrs (
                acc: _roleName: role:
                acc ++ (lib.attrNames role.machines)
              ) [ ] instance.roles
            );
          # The service machines are defined by collecting all instance machines
          # returns "allMachines" that are part of the service in the form:
          # serviceMachines :: { ${machineName} :: MachineOrigin; }
          # MachineOrigin :: { instances :: [ string ]; roles :: [ string ]; }
          serviceMachines = lib.foldlAttrs (
            acc: instanceName: instance:
            acc
            // lib.genAttrs (collectMachinesFromInstance instance) (machineName:
            # Store information why this machine is part of the service
            # MachineOrigin :: { instances :: [ string ]; }
            {
              # Helper attribute to
              instances = [ instanceName ] ++ acc.${machineName}.instances or [ ];
              # All roles of the machine ?
              roles = lib.foldlAttrs (
                acc2: roleName: role:
                if builtins.elem machineName (lib.attrNames role.machines) then acc2 ++ [ roleName ] else acc2
              ) [ ] instance.roles;
            })
          ) { } config.instances;

          allMachines = lib.mapAttrs (_machineName: MachineOrigin: {
            # Filter out instances of which the machine is not part of
            instances = lib.mapAttrs (_n: v: { roles = v; }) (
              lib.filterAttrs (instanceName: _: builtins.elem instanceName MachineOrigin.instances) (
                # Instances with evaluated settings
                lib.mapAttrs applySettings config.instances
              )
            );
          }) serviceMachines;
        in
        # allMachines;
        lib.mapAttrs config.perMachine allMachines;
    };

    result.final = mkOption {
      visible = false;
      readOnly = true;
      default = lib.mapAttrs (
        machineName: machineResult:
        let
          instanceResults = lib.foldlAttrs (
            acc: roleName: role:
            acc
            ++ lib.foldlAttrs (
              acc: instanceName: instance:
              if instance.allMachines.${machineName}.nixosModule or { } != { } then
                acc
                ++ [
                  (lib.setDefaultModuleLocation
                    "Via instances.${instanceName}.roles.${roleName}.machines.${machineName}"
                    instance.allMachines.${machineName}.nixosModule
                  )
                ]
              else
                acc
            ) [ ] role.allInstances
          ) [ ] config.result.allRoles;
        in
        {
          inherit instanceResults;
          nixosModule = {
            imports = [
              # include service assertions:
              (
                let
                  failedAssertions = (lib.filterAttrs (_: v: !v.assertion) config.result.assertions);
                in
                {
                  assertions = lib.attrValues failedAssertions;
                }
              )

              # For error backtracing. This module was produced by the 'perMachine' function
              # TODO: check if we need this or if it leads to better errors if we pass the underlying module locations
              # (lib.setDefaultModuleLocation "clan.service: ${config.manifest.name} - via perMachine" machineResult.nixosModule)
              (machineResult.nixosModule)
            ] ++ instanceResults;
          };
        }
      ) config.result.allMachines;
    };
  };
}
