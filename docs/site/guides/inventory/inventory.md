
`Inventory` is an abstract service layer for consistently configuring distributed services across machine boundaries.

## Concept

Its concept is slightly different to what NixOS veterans might be used to. The inventory is a service definition on a higher level, not a machine configuration. This allows you to define a consistent and coherent service.

The inventory logic will automatically derive the modules and configurations to enable on each machine in your `clan` based on its `role`. This makes it super easy to setup distributed `services` such as Backups, Networking, traditional cloud services, or peer-to-peer based applications.

The following tutorial will walk through setting up a Backup service where the terms `Service` and `Role` will become more clear.

!!! example "Experimental status"
    The inventory implementation is not considered stable yet.
    We are actively soliciting feedback from users.

    Stabilizing the API is a priority.

## Prerequisites

- [x] [Add some machines](../../getting-started/add-machines.md) to your Clan.

## Services

The inventory defines `instances` of clan services. Membership of `machines` is defined via `roles` exclusively.

See each [modules documentation](../../services/official/index.md) for its available roles.

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
