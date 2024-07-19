# Nix API Overview

There are two top-level components of the Nix API, which together allow for the declarative definition of a Clan:

- the [Inventory](./inventory.md), a structure representing the machines, services, custom configurations, and other data that constitute a Clan, and
- the [`buildClan`](./buildclan.md) function, which constructs a Clan from an Inventory definition.
