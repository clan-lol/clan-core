# Next (unreleased)

<!-- Release notes for the next, not-yet-scheduled stable release.
     Rename this file to the version (e.g. 26-11.md) once the release is cut. -->

## Breaking Changes

### `users`: `prompt` now defaults to `false`

The `users` service now generates a random password instead of prompting for
one. Already generated passwords are unaffected. Set
`roles.default.settings.prompt = true` to keep being prompted when adding new
machines.

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

### New clans use the age vars backend

The `default` clan template used by `clan init` is simpler and selects the
[age backend](/docs/guides/vars/age/age-backend) for secrets
(`vars.settings.secretStore = "age"`). `clan init` writes the public key of
your selected or newly generated age key into
`vars.settings.recipients.default`, instead of creating a sops user under
`sops/users/`. Templates that keep the sops backend (e.g. `minimal`) still get
a sops user. The template also enables the experimental `p2p-ssh-iroh`
service on all machines, so `clan ssh` and `clan machines update` reach
installed machines without configuring an IP address. The unused
`modules/gnome.nix` example was dropped from the template. Existing clans are
unaffected.

## Fixes

### yggdrasil: multicast peer discovery now actually on by default

The empty `multicastInterfaces` default silently disabled multicast peer
discovery. It is now enabled on all interfaces by default, with direct
local links preferred over overlay interfaces and static peers. Set
`settings.multicastInterfaces = [ ]` to opt out.

## Changes

### p2p-ssh-iroh is no longer experimental

The `p2p-ssh-iroh` service is now considered stable. Its experimental
warnings have been removed from the service and networking docs.
