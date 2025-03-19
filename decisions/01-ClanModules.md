# Clan service modules

Status: Accepted

## Context

To define a service in Clan, you need to define two things:

- `clanModule` - defined by module authors
- `inventory` - defined by users

The `clanModule` is currently a plain NixOS module. It is conditionally imported into each machine depending on the `service` and `role`.

A `role` is a function of a machine within a service. For example in the `backup` service there are `client` and `server` roles.

The `inventory` contains the settings for the user/consumer of the module. It describes what `services` run on each machine and with which `roles`.

Additionally any `service` can be instantiated multiple times.

This ADR proposes that we change how to write a `clanModule`. The `inventory` should get a new attribute called `instances` that allow for configuration of these modules.

### Status Quo

In this example the user configures 2 instances of the `networking` service:

The *user* defines

```nix
{
  inventory.services = {
    # anything inside an instance is instance specific
    networking."instance1" = {
      roles.client.tags = [ "all" ];
      machines.foo.config = { ... /* machine specific settings */ };

      # this will not apply to `clients` outside of `instance1`
      roles.client.config = { ... /* client specific settings */ };
    };
    networking."instance2" = {
      roles.server.tags = [ "all" ];
      config = { ... /* applies to every machine that runs this instance */ };
    };
  };
}
```

The *module author* defines:

```nix
# networking/roles/client.nix
{ config, ... }:
let
  instances = config.clan.inventory.services.networking or { };

  serviceConfig = config.clan.networking;
in {
  ## Set some nixos options
}
```

### Problems

Problems with the current way of writing clanModules:

1. No way to retrieve the config of a single service instance, together with its name.
2. Directly exporting a single, anonymous nixosModule without any intermediary attribute layers doesn't leave room for exporting other inventory resources such as potentially `vars` or `homeManagerConfig`.
3. Can't access multiple config instances individually.
   Example:
   ```nix
   inventory = {
      services = {
        network.c-base = {
          instanceConfig.ips = {
            mors = "172.139.0.2";
          };
        };
        network.gg23 = {
          instanceConfig.ips = {
            mors = "10.23.0.2";
          };
        };
      };
    };
   ```
   This doesn't work because all instance configs are applied to the same namespace. So this results in a conflict currently.
   Resolving this problem means that new inventory modules cannot be plain nixos modules anymore. If they are configured via `instances` / `instanceConfig` they cannot be configured without using the inventory. (There might be ways to inject instanceConfig but that requires knowledge of inventory internals)

4. Writing modules for multiple instances is cumbersome. Currently the clanModule author has to write one or multiple `fold` operations for potentially every nixos option to define how multiple service instances merge into every single one option. The new idea behind this adr is to pull the common fold function into the outer context provide it as a common helper. (See the example below. `perInstance` analog to the well known `perSystem` of flake-parts)

5. Each role has a different interface. We need to render that interface into json-schema which includes creating an unnecessary test machine currently. Defining the interface at a higher level (outside of any machine context) allows faster evaluation and an isolation by design from any machine.
This allows rendering the UI (options tree) of a service by just knowing the service and the corresponding roles without creating a dummy machine.

6. The interface of defining config is wrong. It is possible to define config that applies to multiple machine at once. It is possible to define config that applies to
a machine as a hole. But this is wrong behavior because the options exist at the role level. So config must also always exist at the role level.
Currently we merge options and config together but that may produce conflicts. Those module system conflicts are very hard to foresee since they depend on what roles exist at runtime.

## Proposed Change

We will create a new module class which is defined by `_class = "clan.service"` ([documented here](https://nixos.org/manual/nixpkgs/stable/#module-system-lib-evalModules-param-class)).

Existing clan modules will still work by continuing to be plain NixOS modules. All new modules can set `_class = "clan.service";` to use the proposed features.

In short the change introduces a new module class that makes the currently necessary folding of `clan.service`s `instances` and `roles` a common operation. The module author can define the inner function of the fold operations which is called a `clan.service` module.

There are the following attributes of such a module:

### `roles.<roleName>.interface`

Each role can have a different interface for how to be configured.
I.e.: A `client` role might have different options than a `server` role.

This attribute should be used to define `options`. (Not `config` !)

The end-user defines the corresponding `config`.

This submodule will be evaluated for each `instance role` combination and passed as argument into `perInstance`.

This submodules `options` will be evaluated to build the UI for that module dynamically.

### **Result attributes**

Some common result attributes are produced by modules of this proposal, those will be referenced later in this document but are commonly defined as:

- `nixosModule` A single nixos module. (`{config, ...}:{ environment.systemPackages = []; }`)
- `services.<serviceName>` An attribute set of `_class = clan.service`. Which contain the same thing as this whole ADR proposes.
- `vars` To be defined. Reserved for now.

### `roles.<roleName>.perInstance`

This acts like a function that maps over all `service instances` of a given `role`.
It produces the previously defined **result attributes**.

I.e. This allows to produce multiple `nixosModules` one for every instance of the service.
Hence making multiple `service instances` convenient by leveraging the module-system merge behavior.

### `perMachine`

This acts like a function that maps over all `machines` of a given `service`.
It produces the previously defined **result attributes**.

I.e. this allows to produce exactly one `nixosModule` per `service`.
Making it easy to set nixos-options only once if they have a one-to-one relation to a service being enabled.

Note: `lib.mkIf` can be used on i.e. `roleName` to make the scope more specific.

### `services.<serviceName>`

This allows to define nested services.
i.e the *service* `backup` might define a nested *service* `ssh` which sets up an ssh connection.

This can be defined in `perMachine` and `perInstance`

- For Every `instance` a given `service` may add multiple nested `services`.
- A given `service` may add a static set of nested `services`; Even if there are multiple instances of the same given service.

Q: Why is this not a top-level attribute?
A: Because nested service definitions may also depend on a `role` which must be resolved depending on `machine` and `instance`. The top-level module doesn't know anything about machines. Keeping the service layer machine agnostic allows us to build the UI for a module without adding any machines. (One of the problems with the current system)

```
zerotier/default.nix
```
```nix
# Some example module
{
  _class = "clan.service";

  # Analog to flake-parts 'perSystem' only that it takes instance
  # The exact arguments will be specified and documented along with the actual implementation.
  roles.client.perInstance = {
      # attrs : settings of that instance
      settings,
      # string : name of the instance
      instanceName,
      # { name :: string , roles :: listOf string; }
      machine,
      # { {roleName} :: { machines :: listOf string; } }
      roles,
      ...
    }:
    {
      # Return a nixos module for every instance.
      # The module author must be aware that this may return multiple modules (one for every instance) which are merged natively
      nixosModule = {
        config.debug."${instanceName}-client" = instanceConfig;
      };
    };
  # Function that is called once for every machine with the role "client"
  # Receives at least the following parameters:
  #
  # machine :: { name :: String, roles :: listOf string; }
  # Name of the machine
  #
  # instances :: { instanceName :: { roleName :: { machines :: [ string ]; }}}
  # Resolved roles
  # Same type as currently in `clan.inventory.services.<ServiceName>.<InstanceName>.roles`
  #
  # The exact arguments will be specified and documented along with the actual implementation.
  perMachine = {machine, instances, ... }: {
    nixosModule =
      { lib, ... }:
      {
        # Some shared code should be put into a shared file
        # Which is then imported into all/some roles
        imports = [
          ../shared.nix
        ] ++
        (lib.optional (builtins.elem "client" machine.roles)
        {
          options.debug = lib.mkOption {
            type = lib.types.attrsOf lib.types.raw;
          };
        });
      };
  };
}
```

## Inventory.instances

This document also proposes to add a new attribute to the inventory that allow for exclusive configuration of the new modules.
This allows to better separate the new and the old way of writing and configuring modules. Keeping the new implementation more focussed and keeping existing technical debt out from the beginning.

The following thoughts went into this:

- Getting rid of `<serviceName>`: Using only the attribute name (plain string) is not sufficient for defining the source of the service module. Encoding meta information into it would also require some extensible format specification and parser.
- removing instanceConfig and machineConfig: There is no such config. Service configuration must always be role specific, because the options are defined on the role.
- renaming `config` to `settings` or similar. Since `config` is a module system internal name.
- Tags and machines should be an attribute set to allow setting `settings` on that level instead.

```nix
{
  inventory.instances = {
    "instance1" = {
      # Allows to define where the module should be imported from.
      module = {
        input = "clan-core";
        name = "borgbackup";
      };
      # settings that apply to all client machines
      roles.client.settings = {};
      # settings that apply to the client service of machine with name <machineName>
      # There might be a server service that takes different settings on the same machine!
      roles.client.machines.<machineName>.settings = {};
      # settings that apply to all client-instances with tag <tagName>
      roles.client.tags.<tagName>.settings = {};
    };
    "instance2" = {
      # ...
    };
  };
}

```

## Iteration note

We want to implement the system as described. Once we have sufficient data on real world use-cases and modules we might revisit this document along with the updated implementation.


## Real world example

The following module demonstrates the idea in the example of *borgbackup*.

```nix
{
  _class = "clan.service";

  # Define the 'options' of 'settings' see argument of perInstance
  roles.server.interface =
    { lib, ... }:
    {
      options = lib.mkOption {
        type = lib.types.str;
        default = "/var/lib/borgbackup";
        description = ''
          The directory where the borgbackup repositories are stored.
        '';
      };
    };

  roles.server.perInstance =
    {
      instanceName,
      settings,
      roles,
      ...
    }:
    {
      nixosModule =
        { config, lib, ... }:
        let
          dir = config.clan.core.settings.directory;
          machineDir = dir + "/vars/per-machine/";
          allClients = roles.client.machines;
        in
        {
          # services.borgbackup is a native nixos option
          config.services.borgbackup.repos =
            let
              borgbackupIpMachinePath = machine: machineDir + machine + "/borgbackup/borgbackup.ssh.pub/value";

              machinesMaybeKey = builtins.map (
                machine:
                let
                  fullPath = borgbackupIpMachinePath machine;
                in
                if builtins.pathExists fullPath then
                  machine
                else
                  lib.warn ''
                    Machine ${machine} does not have a borgbackup key at ${fullPath},
                    run `clan var generate ${machine}` to generate it.
                  '' null
              ) allClients;

              machinesWithKey = lib.filter (x: x != null) machinesMaybeKey;

              hosts = builtins.map (machine: {
                name = instanceName + machine;
                value = {
                  path = "${settings.directory}/${machine}";
                  authorizedKeys = [ (builtins.readFile (borgbackupIpMachinePath machine)) ];
                };
              }) machinesWithKey;
            in
            if (builtins.listToAttrs hosts) != [ ] then builtins.listToAttrs hosts else { };
        };
    };

  roles.client.interface =
    { lib, ... }:
    {
      # There might be a better interface now. This is just how clan borgbackup was configured in the 'old' way
      options.destinations = lib.mkOption {
        type = lib.types.attrsOf (
          lib.types.submodule (
            { name, ... }:
            {
              options = {
                name = lib.mkOption {
                  type = lib.types.strMatching "^[a-zA-Z0-9._-]+$";
                  default = name;
                  description = "the name of the backup job";
                };
                repo = lib.mkOption {
                  type = lib.types.str;
                  description = "the borgbackup repository to backup to";
                };
                rsh = lib.mkOption {
                  type = lib.types.nullOr lib.types.str;
                  default = null;
                  defaultText = "ssh -i \${config.clan.core.vars.generators.borgbackup.files.\"borgbackup.ssh\".path} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null";
                  description = "the rsh to use for the backup";
                };
              };
            }
          )
        );
        default = { };
        description = ''
          destinations where the machine should be backed up to
        '';
      };

      options.exclude = lib.mkOption {
        type = lib.types.listOf lib.types.str;
        example = [ "*.pyc" ];
        default = [ ];
        description = ''
          Directories/Files to exclude from the backup.
          Use * as a wildcard.
        '';
      };
    };
  roles.client.perInstance =
    {
      instanceName,
      roles,
      machine,
      settings,
      ...
    }:
    {
      nixosModule =
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          allServers = roles.server.machines;

          # machineName = config.clan.core.settings.machine.name;

          # cfg = config.clan.borgbackup;
          preBackupScript = ''
            declare -A preCommandErrors

            ${lib.concatMapStringsSep "\n" (
              state:
              lib.optionalString (state.preBackupCommand != null) ''
                echo "Running pre-backup command for ${state.name}"
                if ! /run/current-system/sw/bin/${state.preBackupCommand}; then
                  preCommandErrors["${state.name}"]=1
                fi
              ''
            ) (lib.attrValues config.clan.core.state)}

            if [[ ''${#preCommandErrors[@]} -gt 0 ]]; then
              echo "pre-backup commands failed for the following services:"
              for state in "''${!preCommandErrors[@]}"; do
                echo "  $state"
              done
              exit 1
            fi
          '';

          destinations =
            let
              destList = builtins.map (serverName: {
                name = "${instanceName}-${serverName}";
                value = {
                  repo = "borg@${serverName}:/var/lib/borgbackup/${machine.name}";
                  rsh = "ssh -i ${
                    config.clan.core.vars.generators."borgbackup-${instanceName}".files."borgbackup.ssh".path
                  } -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o IdentitiesOnly=Yes";
                } // settings.destinations.${serverName};
              }) allServers;
            in
            (builtins.listToAttrs destList);
        in
        {
          config = {
            # Derived from the destinations
            systemd.services = lib.mapAttrs' (
              _: dest:
              lib.nameValuePair "borgbackup-job-${instanceName}-${dest.name}" {
                # since borgbackup mounts the system read-only, we need to run in a ExecStartPre script, so we can generate additional files.
                serviceConfig.ExecStartPre = [
                  ''+${pkgs.writeShellScript "borgbackup-job-${dest.name}-pre-backup-commands" preBackupScript}''
                ];
              }
            ) destinations;

            services.borgbackup.jobs = lib.mapAttrs (_destinationName: dest: {
              paths = lib.unique (
                lib.flatten (map (state: state.folders) (lib.attrValues config.clan.core.state))
              );
              exclude = settings.exclude;
              repo = dest.repo;
              environment.BORG_RSH = dest.rsh;
              compression = "auto,zstd";
              startAt = "*-*-* 01:00:00";
              persistentTimer = true;

              encryption = {
                mode = "repokey";
                passCommand = "cat ${config.clan.core.vars.generators."borgbackup-${instanceName}".files."borgbackup.repokey".path}";
              };

              prune.keep = {
                within = "1d"; # Keep all archives from the last day
                daily = 7;
                weekly = 4;
                monthly = 0;
              };
            }) destinations;

            environment.systemPackages = [
              (pkgs.writeShellApplication {
                name = "borgbackup-create";
                runtimeInputs = [ config.systemd.package ];
                text = ''
                  ${lib.concatMapStringsSep "\n" (dest: ''
                    systemctl start borgbackup-job-${dest.name}
                  '') (lib.attrValues destinations)}
                '';
              })
              (pkgs.writeShellApplication {
                name = "borgbackup-list";
                runtimeInputs = [ pkgs.jq ];
                text = ''
                  (${
                    lib.concatMapStringsSep "\n" (
                      dest:
                      # we need yes here to skip the changed url verification
                      ''echo y | /run/current-system/sw/bin/borg-job-${dest.name} list --json | jq '[.archives[] | {"name": ("${dest.name}::${dest.repo}::" + .name)}]' ''
                    ) (lib.attrValues destinations)
                  }) | jq -s 'add // []'
                '';
              })
              (pkgs.writeShellApplication {
                name = "borgbackup-restore";
                runtimeInputs = [ pkgs.gawk ];
                text = ''
                  cd /
                  IFS=':' read -ra FOLDER <<< "''${FOLDERS-}"
                  job_name=$(echo "$NAME" | awk -F'::' '{print $1}')
                  backup_name=''${NAME#"$job_name"::}
                  if [[ ! -x /run/current-system/sw/bin/borg-job-"$job_name" ]]; then
                    echo "borg-job-$job_name not found: Backup name is invalid" >&2
                    exit 1
                  fi
                  echo y | /run/current-system/sw/bin/borg-job-"$job_name" extract "$backup_name" "''${FOLDER[@]}"
                '';
              })
            ];
            # every borgbackup instance adds its own vars
            clan.core.vars.generators."borgbackup-${instanceName}" = {
              files."borgbackup.ssh.pub".secret = false;
              files."borgbackup.ssh" = { };
              files."borgbackup.repokey" = { };

              migrateFact = "borgbackup";
              runtimeInputs = [
                pkgs.coreutils
                pkgs.openssh
                pkgs.xkcdpass
              ];
              script = ''
                ssh-keygen -t ed25519 -N "" -f $out/borgbackup.ssh
                xkcdpass -n 4 -d - > $out/borgbackup.repokey
              '';
            };
          };
        };
    };

  perMachine = {
    nixosModule =
      { ... }:
      {
        clan.core.backups.providers.borgbackup = {
          list = "borgbackup-list";
          create = "borgbackup-create";
          restore = "borgbackup-restore";
        };
      };
  };
}
```

## Prior-art

- https://github.com/NixOS/nixops
- https://github.com/infinisil/nixus
