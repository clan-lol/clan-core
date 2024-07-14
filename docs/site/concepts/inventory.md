# Inventory

`Inventory` is an abstract service layer for consistently configuring distributed services across machine boundaries.

## Meta

Metadata about the clan, will be displayed upfront in the upcomming clan-app, make sure to choose a unique name.

```{.nix hl_lines="3-8"}
buildClan {
    inventory = {
        meta = {
            # The following options are available
            # name:        string # Required, name of the clan.
            # description: null | string
            # icon:        null | string
        };
    };
}
```

## Machines

Machines and a small pieve of their configuration can be added via `inventory.machines`.

!!! Note
    It doesn't matter where the machine gets introduced to buildClan - All delarations are valid, duplications are merged.

    However the clan-app (UI) will create machines in the inventory, because it cannot create arbitrary nixos configs.

In the following example `backup_server` is one machine - it may specify parts of its configuration in different places.

```{.nix hl_lines="3-5 12-20"}
buildClan {
    machines = {
        "backup_server" = {
            # Any valid nixos config
        };
        "jon" = {
            # Any valid nixos config
        };
    };
    inventory = {
        machines = {
            "backup_server" = {
                # Don't include any nixos config here
                # The following fields are avilable
                # description: null | string
                # icon:        null | string
                # name:        string
                # system:      null | string
                # tags:        [...string]
            };
            "jon" = {
                # Same as above
            };
        };
    };
}
```

## Services

### Available clanModules

Currently the inventory interface is implemented by the following clanModules

- [borgbackup](../reference/clanModules/borgbackup.md)
- [packages](../reference/clanModules/packages.md)
- [single-disk](../reference/clanModules/single-disk.md)

See the respective module documentation for available roles.

### Adding services to machines

A module can be added to one or multiple machines via `Roles`. clan's `Role` interface provide sane defaults for a module this allows the module author to reduce the configuration overhead to a minimum.

Each service can still be customized and configured according to the modules options.

- Per instance configuration via `services.<serviceName>.<instanceName>.config`
- Per machine configuration via `services.<serviceName>.<instanceName>.machines.<machineName>.config`

### Configuration Examples

!!! Example "Borgbackup Example"

    To configure a service it needs to be added to the machine.
    It is required to assign the service (`borgbackup`) an arbitrary instance name. (`instance_1`)

    See also: [Multiple Service Instances](#multiple-service-instances)

    ```{.nix hl_lines="14-17"}
    buildClan {
        inventory = {
            machines = {
                "backup_server" = {
                    # Don't include any nixos config here
                    # See inventory.Machines for available options
                };
                "jon" = {
                    # Don't include any nixos config here
                    # See inventory.Machines for available options
                };
            };
            services = {
                borgbackup.instance_1 = {
                    roles.client.machines = [ "jon" ];
                    roles.server.machines = [ "backup_server" ];
                };
            };
        };
    }
    ```

!!! Example "Packages Example"

    This example shows how to add `pkgs.firefox` via the inventory interface.

    ```{.nix hl_lines="8-11"}
    buildClan {
        inventory = {
            machines = {
                "sara" = {};
                "jon" = {};
            };
            services = {
                packages.set_1 = {
                    roles.default.machines = [ "jon" "sara" ];
                    # Packages is a configuration option of the "packages" clanModule
                    config.packages = ["firefox"];
                };
            };
        };
    }
    ```

### Tags

It is possible to add services to multiple machines via tags. The service instance gets added in the specified role. In this case `role = "default"`

!!! Example "Tags Example"

    ```{.nix hl_lines="5 8 13"}
    buildClan {
        inventory = {
            machines = {
                "sara" = {
                    tags = ["browsing"];
                };
                "jon" = {
                    tags = ["browsing"];
                };
            };
            services = {
                packages.set_1 = {
                    roles.default.tags = [ "browsing" ];
                    config.packages = ["firefox"];
                };
            };
        };
    }
    ```

### Multiple Service Instances

!!! danger "Important"
    Not all modules support multiple instances yet.

Some modules have support for adding multiple instances of the same service in different roles or configurations.

!!! Example

    In this example `backup_server` has role `client` and `server` in different instances.

    ```{.nix hl_lines="11 14"}
    buildClan {
        inventory = {
            machines = {
                "jon" = {};
                "backup_server" = {};
                "backup_backup_server" = {}
            };
            services = {
                borgbackup.instance_1 = {
                    roles.client.machines = [ "jon" ];
                    roles.server.machines = [ "backup_server" ];
                };
                borgbackup.instance_1 = {
                    roles.client.machines = [ "backup_server" ];
                    roles.server.machines = [ "backup_backup_server" ];
                };
            };
        };
    }
    ```

### Schema specification

The complete schema specification can be retrieved via:

```sh
nix build git+https://git.clan.lol/clan/clan-core#inventory-schema
> result
> ├── schema.cue
> └── schema.json
```
