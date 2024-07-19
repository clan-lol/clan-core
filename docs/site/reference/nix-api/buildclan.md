# buildClan

The core [function](https://git.clan.lol/clan/clan-core/src/branch/main/lib/build-clan/default.nix) that produces a Clan. It returns a set of consistent configurations for all machines with ready-to-use secrets, backups and other services.

## Inputs

`directory`
: The directory containing the machines subdirectory

`machines`
: Allows to include machine-specific modules i.e. machines.${name} = { ... }

`meta`
: An optional set

: `{ name :: string, icon :: string, description :: string }`

`inventory`
: Service set for easily configuring distributed services, such as backups

: For more details see [Inventory](./inventory.md)

`specialArgs`
: Extra arguments to pass to nixosSystem i.e. useful to make self available

`pkgsForSystem`
: A function that maps from architecture to pkgs, if specified this nixpkgs will be only imported once for each system.
  This improves performance, but all nipxkgs.* options will be ignored.
  `(string -> pkgs )`
