# Inventory

`Inventory` is an abstract service layer for consistently configuring distributed services across machine boundaries.

The following is the specification of the inventory in `cuelang`

```cue
{
    meta: {
        // A name of the clan (primarily shown by the UI)
        name: string
        // A description of the clan
        description?: string
        // The icon path
        icon?: string
    }

    // A map of services
    services: [string]: [string]: {
        // Required meta fields
        meta: {
            name: string,
            icon?: string
            description?: string,
        },
        // Machines are added via the avilable roles
        // Membership depends only on this field
        roles: [string]: {
            machines: [...string],
            tags: [...string],
        }
        machines?: {
            [string]: {
                config?: {
                    ...
                }
            }
        },

        // Global Configuration for the service
        // Applied to all machines.
        config?: {
            // Schema depends on the module.
            // It declares the interface how the service can be configured.
            ...
        }
    }
    // A map of machines, extends the machines of `buildClan`
    machines: [string]: {
        name: string,
        description?: string,
        icon?: string
        tags: [...string]
        system: string
    }
}
```
