# Next (unreleased)

<!-- Release notes for the next, not-yet-scheduled stable release.
     Rename this file to the version (e.g. 26-11.md) once the release is cut. -->

## Breaking Changes

### Removed `clan state` subcommand

The `clan state` subcommand has been removed. It only supported listing the
`clan.core.state` folders of a machine. The `clan.core.state` NixOS options
remain unchanged, as backups still rely on them.

### `clan machines generations` up-to-date check removed

`clan machines generations` no longer reports whether a machine is up to date.
That check was based on the telegraf metrics collection, which required the old
monitoring module that no longer exists. The remaining generations listing is
unaffected.

### Removed leftover VM modules

Following the earlier removal of the `vms` subcommand, the remaining dead VM
support code has been dropped, including the `waypipe` NixOS module and the
`system.clan.vm.create` output in `clanCore`.
