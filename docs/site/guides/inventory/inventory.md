
The `Inventory` lets you configure distributed services (backups, networking, peer-to-peer apps, etc.) across multiple machines from a single place.

## Concept

Unlike per-machine NixOS configuration, the inventory defines services at a higher level. Clan automatically derives the modules and settings to enable on each machine based on its `role`, so you only describe the service once.

The following tutorial walks through setting up a Backup service where the terms `Service` and `Role` will become more clear.

!!! example "Experimental status"
    The inventory implementation is not considered stable yet.
    We are actively soliciting feedback from users.

    Stabilizing the API is a priority.

## Prerequisites

- [x] [Add some machines](../../getting-started/add-machines.md) to your Clan.

## Services

The inventory defines `instances` of Clan services. Membership of `machines` is defined via `roles` exclusively.

See each [modules documentation](../../services/definition.md) for its available roles.

### Adding services to machines

A service can be added to one or multiple machines via `Roles`. Clan's `Role` interface provide sane defaults for a module this allows the module author to reduce the configuration overhead to a minimum.

Each service can still be customized and configured according to the modules options.

- Per role configuration via `inventory.instances.<instanceName>.roles.<roleName>.settings`
- Per machine configuration via `inventory.instances.<instanceName>.roles.<roleName>.machines.<machineName>.settings`

### Setting up the Backup Service

!!! Example "Borgbackup Example"

    To configure a service it needs to be added to the machine.
    It is required to assign the service (`borgbackup`) an arbitrary instance name. (`instance_1`)

    See also: [Multiple Service Instances](#multiple-service-instances)

    ```{.nix hl_lines="9-10"}
    {
        inventory.instances.instance_1 = {
            module =  {
                name = "borgbackup";
                input = "clan-core";
            };

            # Machines can be added here.
            roles.client.machines."jon" {};
            roles.server.machines."backup_server" = {};
        };
    }
    ```

### Scaling the Backup

The inventory allows machines to set Tags

It is possible to add services to multiple machines via tags as shown

!!! Example "Tags Example"

    ```{.nix hl_lines="5 8 18"}
    {
        inventory = {
            machines = {
                "jon" = {
                    tags = [ "backup" ];
                };
                "sara" = {
                    tags = [ "backup" ];
                };
            };

            instances.instance_1 = {
                module =  {
                    name = "borgbackup";
                    input = "clan-core";
                };

                roles.client.tags =  [ "backup" ];
                roles.server.machines."backup_server" = {};
            };
        };
    }
    ```

### Multiple Service Instances

!!! danger "Important"
    Not all modules implement support for multiple instances yet.
    Multiple instance usage could create complexity, refer to each modules documentation, for intended usage.

!!! Example

    In this example `backup_server` has role `client` and `server` in different instances.

    ```{.nix hl_lines="17 26"}
    {
        inventory = {
            machines = {
                "jon" = {};
                "backup_server" = {};
                "backup_backup_server" = {};
            };

            instances = {
                instance_1 = {
                    module =  {
                        name = "borgbackup";
                        input = "clan-core";
                    };

                    roles.client.machines."jon" = {};
                    roles.server.machines."backup_server" = {};
                };

                instance_2 = {
                    module =  {
                        name = "borgbackup";
                        input = "clan-core";
                    };

                    roles.client.machines."backup_server" = {};
                    roles.server.machines."backup_backup_server" = {};
                };
            };
        };
    }
    ```
