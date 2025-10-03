**`clanServices`** are modular building blocks that simplify the configuration and orchestration of multi-host services.

Each `clanService`:

* Is a module of class **`clan.service`**
* Can define **roles** (e.g., `client`, `server`)
* Uses **`inventory.instances`** to configure where and how it is deployed

!!! Note
    `clanServices` are part of Clan's next-generation service model and are intended to replace `clanModules`.

    See [Migration Guide](../guides/migrations/migrate-inventory-services.md) for help on migrating.

Learn how to use `clanServices` in practice in the [Using clanServices guide](../guides/services/introduction-to-services.md).
