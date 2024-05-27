# Clan module maintaining

## General Description

Clan modules are pieces of software that can be used by admins to build a private or public infrastructure.

Clan modules should have the following properties:

1. Documented: It should be clear what the module does and how to use it.
1. Self contained: A module should be usable as is. If it requires any other software or settings, those should be delivered with the module itself.
1. Simple to deploy and use: Modules should have opinionated defaults that just work. Any customization should be optional

## Stories

### Story 1: Maintaining a shared folder module

Alice maintains a module for a shared folder service that she uses in her own infra, but also publishes for the community.

By following clan module standards (Backups, Interfaces, Output schema, etc), other community members have an easy time re-using the module within their own infra.

She benefits from publishing the module, because other community members start using it and help to maintain it.

## Challenges

...
