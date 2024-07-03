# Configuration

## Introduction

When managing machine configuration this can be done through many possible ways.
Ranging from writing `nix` expression in a `flake.nix` file; placing `autoincluded` files into your machine directory; or configuring everything in a simple UI (upcomming).

clan currently offers the following methods to configure machines:

!!! Success "Recommended for nix people"

    - flake.nix (i.e. via `buildClan`)
        - `machine` argument
        - `inventory` argument

    - machines/`machine_name`/configuration.nix (`autoincluded` if it exists)

???+ Note "Used by CLI & UI"

    - inventory.json
    - machines/`machine_name`/hardware-configuration.nix (`autoincluded` if it exists)


!!! Warning "Deprecated"

    machines/`machine_name`/settings.json

## BuildClan

The core function that produces a clan. It returns a set of consistent configurations for all machines with ready-to-use secrets, backups and other services.

### Inputs

`directory`
: The directory containing the machines subdirectory

`machines`
: Allows to include machine-specific modules i.e. machines.${name} = { ... }

`meta`
: An optional set

: `{ name :: string, icon :: string, description :: string }`

`inventory`
: Service set for easily configuring distributed services, such as backups

: For more details see [Inventory](#inventory)

`specialArgs`
: Extra arguments to pass to nixosSystem i.e. useful to make self available

`pkgsForSystem`
: A function that maps from architecture to pkgs, if specified this nixpkgs will be only imported once for each system.
  This improves performance, but all nipxkgs.* options will be ignored.
  `(string -> pkgs )`

## Inventory

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
