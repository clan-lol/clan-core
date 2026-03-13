# Definition

**`clanServices`** are modular building blocks that simplify the configuration and orchestration of multi-host services.

Each `clanService`:

* Is a module of class **`clan.service`**
* Can define **roles** (e.g., `client`, `server`)
* Uses **`inventory.instances`** to configure where and how it is deployed

:::admonition[Note]{type=note}
`clanServices` are part of Clan's next-generation service model and are intended to replace `clanModules`.

See [Migration Guide](/docs/guides/migrations/migrate-inventory-services) for help on migrating.
:::

Learn how to use `clanServices` in practice in the [Using clanServices guide](/docs/guides/services/intro-to-services-revised).
