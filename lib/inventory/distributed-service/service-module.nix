{
  lib,
  config,
  _ctx,
  directory,
  exports,
  ...
}:
let
  inherit (lib) mkOption types;
  inherit (types) attrsWith submoduleWith;

  errorContext = "Error context: ${lib.concatStringsSep "." _ctx}";
  # TODO:
  # Remove once this gets merged upstream; performs in O(n*log(n) instead of O(n^2))
  # https://github.com/NixOS/nixpkgs/pull/355616/files
  uniqueStrings = list: builtins.attrNames (builtins.groupBy lib.id list);
  /**
    Merges the role- and machine-settings using the role interface

    Arguments:

    - roleName: The name of the role
    - instanceName: The name of the instance
    - : The settings of the machine. Leave empty to get the role settings
    - modules: The settings of the machine. Leave empty to get the role settings

    Returns: evalModules result

    The caller is responsible to use .config or .extendModules
  */
  evalMachineSettings =
    instanceName: roleName: machineName: roleSettings: machineSettings:
    lib.evalModules {
      # Prefix for better error reporting
      # This prints the path where the option should be defined rather than the plain path within settings
      # "The option `instances.foo.roles.server.machines.test.settings.<>' was accessed but has no value defined. Try setting the option."
      prefix =
        _ctx
        ++ [
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
        (lib.setDefaultModuleLocation "Via clan.service module: instances.${instanceName}.roles.${roleName}.settings" roleSettings)
        machineSettings
      ];
    };

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
      settings = config.instances.${instanceName}.roles.${roleName}.finalSettings.config;
      machines = lib.mapAttrs (machineName: _v: {
        settings =
          config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.finalSettings.config;
      }) role.machines;
    }) instance.roles;
in
{
  options = {
    # Option to disable some behavior during docs rendering
    _docs_rendering = mkOption {
      default = false;
      visible = false;
      type = types.bool;
    };

    instances = mkOption {
      visible = false;
      defaultText = "Throws: 'The service must define its instances' when not defined";
      default = throw ''
        The clan service module ${config.manifest.name} doesn't define any instances.

        Did you forget to create instances via 'instances'?

        ${errorContext}
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
              { name, ... }@instance:
              {
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
                    'instances.${name}.roles.<role-name>.machines.<machine-name>' must be set.

                    ${errorContext}
                  '';
                  type = attrsWith {
                    placeholder = "roleName";
                    elemType = submoduleWith {
                      modules = [
                        (
                          { name, ... }@role:
                          {
                            options.finalSettings = mkOption {
                              default = evalMachineSettings instance.name role.name null role.config.settings { };
                              type = types.raw;
                              description = ''
                                Final evaluated settings of the curent-machine

                                This contains the merged and evaluated settings of the role interface,
                                the role settings and the machine settings.

                                Type: 'configuration' as returned by 'lib.evalModules'
                              '';
                              apply = lib.warn ''
                                === WANRING ===
                                'roles.<roleName>.settings' do not contain machine specific settings.

                                Prefer `machines.<machineName>.settings` instead. (i.e `perInstance: roles.<roleName>.machines.<machineName>.settings`)

                                If you have a use-case that requires access to the original role settings without machine overrides.
                                Contact us via matrix (https://matrix.to/#/#clan:clan.lol) or file an issue: https://git.clan.lol

                                This feature will be removed in the next release
                              '';
                            };
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
                                    (
                                      { name, ... }@machine:
                                      {
                                        options.settings = mkOption {
                                          type = types.raw;
                                          description = "Settings of '${name}-machine': ${machine.name or "<machineName>"}.";
                                          default = { };
                                        };
                                        options.finalSettings = mkOption {
                                          default =
                                            evalMachineSettings instance.name role.name machine.name role.config.settings
                                              machine.config.settings;
                                          type = types.raw;
                                          description = ''
                                            Final evaluated settings of the curent-machine

                                            This contains the merged and evaluated settings of the role interface,
                                            the role settings and the machine settings.

                                            Type: 'configuration' as returned by 'lib.evalModules'
                                          '';
                                        };
                                      }
                                    )
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
                              type = types.listOf types.deferredModule;
                            };
                          }
                        )
                      ];
                    };
                  };
                  apply =
                    v:
                    lib.seq (
                      (

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
                            Instance: 'instances.${instanceName}' uses the following roles:
                            ${builtins.toJSON unmatchedRoles}

                            But the clan-service module '${config.manifest.name}' only defines roles:
                            ${builtins.toJSON (lib.attrNames config.roles)}

                            ${errorContext}
                          ''

                      )
                      name
                      v
                    ) v;
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
          {
            options = {
              name = mkOption {
                description = ''
                  The name of the module

                  Mainly used to create an error context while evaluating.
                  This helps backtracking which module was included; And where an error came from originally.
                '';
                type = types.str;
              };
              description = mkOption {
                type = types.str;
                description = ''
                  A Short description of the module.
                '';
                default = "No description";
              };
              readme = mkOption {
                type = types.str;
                description = ''
                  Extended usage description
                '';
                default = "";
              };
              categories = mkOption {
                default = [ "Uncategorized" ];
                description = ''
                  Categories are used for Grouping and searching.

                  While initial oriented on [freedesktop](https://specifications.freedesktop.org/menu-spec/latest/category-registry.html) the following categories are allowed
                '';
                type = types.listOf (
                  types.enum [
                    "Audio"
                    "AudioVideo"
                    "Desktop"
                    "Development"
                    "Education"
                    "Game"
                    "Graphics"
                    "Network"
                    "Office"
                    "Science"
                    "Settings"
                    "Social"
                    "System"
                    "Uncategorized"
                    "Utility"
                    "Video"
                  ]
                );
              };

              features = mkOption {
                description = ''
                  Enable built-in features for the module

                  See the documentation for each feature:
                  - API
                '';
                type = types.submoduleWith {
                  modules = [
                    {
                      options.API = mkOption {
                        type = types.bool;
                        # This is read only, because we don't support turning it off yet
                        readOnly = true;
                        default = true;
                        description = ''
                          Enables automatic API schema conversion for the interface of this module.
                        '';
                      };
                    }
                  ];
                };
                default = { };
              };
            };
          }
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

        ${errorContext}
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
                options.description = mkOption {
                  type = lib.types.nullOr types.str;
                  description = "A short description of the role '${name}', explaining it's effect on the supplied machine.";
                  example = "Connects the supplied machine as a '${name}' to the 'example' service.";
                  default = null;
                };

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
                        };
                        # ...
                      };
                      ```

                    - `settings`: The settings of the current machine, as defined in `instances`
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
                        options.exports = mkOption {
                          type = types.deferredModule;
                          default = { };
                          description = ''
                            !!! Danger "Experimental Feature"
                                This feature is experimental and will change in the future.

                            export modules defined in 'perInstance'
                            mapped to their instance name

                            Example

                            with instances:

                            ```nix
                            instances.A = { ... };
                            instances.B= { ... };

                            roles.peer.perInstance = { instanceName, machine, ... }:
                            {
                              exports.foo = 1;
                            }

                            This yields all other services can access these exports
                            =>
                            exports.instances.A.foo = 1;
                            exports.instances.B.foo = 1;
                            ```
                          '';
                        };
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
                          inherit instanceName roles exports;
                          machine = {
                            name = machineName;
                            roles = lib.attrNames (lib.filterAttrs (_n: v: v.machines ? ${machineName}) roles);
                          };
                          settings =
                            config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.finalSettings.config;
                          extendSettings =
                            extendEval
                              config.instances.${instanceName}.roles.${roleName}.machines.${machineName}.finalSettings;
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
                    # Resolved per-machine settings
                    machines = { <machineName> = { settings = { ... }; }; }; };
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
            options.exports = mkOption {
              type = types.deferredModule;
              default = { };
              description = ''
                !!! Danger "Experimental Feature"
                    This feature is experimental and will change in the future.

                export modules defined in 'perMachine'
                mapped to their machine name

                Example

                with machines:
                ```nix
                instances.A = { roles.peer.machines.jon = ... };
                instances.B = { roles.peer.machines.jon = ... };

                perMachine = { machine, ... }:
                {
                  exports.foo = 1;
                }

                This yields all other services can access these exports
                =>
                exports.machines.jon.foo = 1;
                exports.machines.sara.foo = 1;
                ```
              '';
            };
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
            inherit exports;
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

              ${errorContext}
            '';
          };

          modules = [ v ];
        }).config;
    };

    exports = mkOption {
      description = ''
        !!! Danger "Experimental Feature"
            This feature is experimental and will change in the future.

        This services exports.
        Gets merged with all other services exports.

        Exports are used to share and expose information between instances.

        Define exports in the [`perInstance`](#roles.perInstance) or [`perMachine`](#perMachine) scope.

        Accessing the exports:

        ```nix
        { exports, ... }: {
          _class = "clan.service";

          # ...
          roles.peer.perInstance = { exports, ...}: { ...};

          # ...
          perMachine = { exports, ...}: { ...};
        }
        ```
      '';
      default = { };
      type = types.submoduleWith {
        # Static modules
        modules = [
          {
            options.instances = mkOption {
              type = types.attrsOf types.deferredModule;
              description = ''
                export modules defined in 'perInstance'
                mapped to their instance name

                Example

                with instances:

                ```nix
                instances.A = { ... };
                instances.B= { ... };

                roles.peer.perInstance = { instanceName, machine, ... }:
                {
                  exports.foo = 1;
                }

                This yields all other services can access these exports
                =>
                exports.instances.A.foo = 1;
                exports.instances.B.foo = 1;
                ```
              '';
            };
            options.machines = mkOption {
              type = types.attrsOf types.deferredModule;
              description = ''
                export modules defined in 'perMachine'
                mapped to their machine name

                Example

                with machines:

                ```nix
                instances.A = { roles.peer.machines.jon = ... };
                instances.B = { roles.peer.machines.jon = ... };

                perMachine = { machine, ... }:
                {
                  exports.foo = 1;
                }

                This yields all other services can access these exports
                =>
                exports.machines.jon.foo = 1;
                exports.machines.sara.foo = 1;
                ```
              '';
            };
            # Lazy default via imports
            # should probably be moved to deferredModuleWith { staticModules = [ ]; }
            imports =
              if config._docs_rendering then
                [ ]
              else
                lib.mapAttrsToList (_roleName: role: {
                  instances = lib.mapAttrs (_instanceName: instance: {
                    imports = lib.mapAttrsToList (_machineName: v: v.exports) instance.allMachines;
                  }) role.allInstances;
                }) config.result.allRoles
                ++ lib.mapAttrsToList (machineName: machine: {
                  machines.${machineName} = machine.exports;
                }) config.result.allMachines;
          }
        ];
      };
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
                  services :: { };
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
            instanceRes
            // {
              nixosModule = {
                imports = [
                  # Result of the applied 'perInstance = {...}: {  nixosModule = { ... }; }'
                  instanceRes.nixosModule
                ]
                ++ (map (
                  s: if builtins.typeOf s == "string" then "${directory}/${s}" else s
                ) instanceCfg.roles.${roleName}.extraModules);
              };
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

    # The result collected from 'perMachine'
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
          instanceResults =
            lib.foldlAttrs
              (
                roleAcc: roleName: role:
                roleAcc
                // lib.foldlAttrs (
                  instanceAcc: instanceName: instance:
                  instanceAcc
                  // {
                    nixosModules = (
                      if instance.allMachines.${machineName}.nixosModule or { } != { } then
                        instanceAcc.nixosModules
                        ++ [
                          (lib.setDefaultModuleLocation
                            "Via instances.${instanceName}.roles.${roleName}.machines.${machineName}"
                            instance.allMachines.${machineName}.nixosModule
                          )
                        ]
                      else
                        instanceAcc.nixosModules
                    );
                  }
                ) roleAcc role.allInstances
              )
              {
                nixosModules = [ ];
                # ...
              }
              config.result.allRoles;
        in
        {
          inherit instanceResults machineResult;
          nixosModule = {
            imports = [
              # include service assertions:
              (
                let
                  failedAssertions = (lib.filterAttrs (_: v: !v.assertion) config.result.assertions);
                  formatModule =
                    if config.module.input != null then
                      "${config.module.input}/${config.module.name}"
                    else
                      "<clan-core>/${config.module.name}";
                  warningsWithNull = lib.mapAttrsToList (
                    roleName: roleConfig:
                    if (roleConfig.description == null) then
                      "Missing description for role '${roleName}' of clanService '${formatModule}'"
                    else
                      null
                  ) config.roles;
                  manifestWarnings = lib.optionals (config.manifest.readme == null || config.manifest.readme == "") [
                    "Missing manifest.readme for clanService '${formatModule}'"
                  ];
                in
                {
                  warnings = (lib.filter (v: v != null) warningsWithNull ++ manifestWarnings);
                  assertions = lib.attrValues failedAssertions;
                }
              )
              (lib.setDefaultModuleLocation "Via ${config.manifest.name}.perMachine - machine='${machineName}';" machineResult.nixosModule)
            ]
            ++ instanceResults.nixosModules;
          };
        }
      ) config.result.allMachines;
    };
  };
}
