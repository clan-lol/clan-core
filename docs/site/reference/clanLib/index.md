`clanLib` is a collection of functions and utilities

!!! Danger
    unless explicitly mentioned everything in ClanLib is for internal use in clan-core.

## Stable Attributes

The following attributes are publicly maintained

### `clanLib.clan`

A function that takes [Clan options](../../reference/options/clan.md)
The option definitions can be composed by means of `imports`

Returns an evaluated Clan configuration - A `lib.evalModules` result:

- `.config`: *The main result*
- `.options`,`.moduleGraph`, ...: For debugging.