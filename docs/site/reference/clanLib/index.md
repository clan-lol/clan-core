# Clanlib

`clanLib` is a collection of functions and utilities

:::admonition[Danger]{type=danger}
unless explicitly mentioned everything in ClanLib is for internal use in clan-core.
:::

## Stable Attributes

The following attributes are publicly maintained

### `clanLib.clan`

A function that takes [Clan options](/docs/reference/options/clan)
The option definitions can be composed by means of `imports`

Returns an evaluated Clan configuration - A `lib.evalModules` result:

- `.config`: *The main result*
- `.options`,`.moduleGraph`, ...: For debugging.
