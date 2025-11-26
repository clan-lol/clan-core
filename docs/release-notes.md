# clan-core release notes 25.11

<!-- This is not rendered yet -->

## New features

Exports
- Standardized exports system with centrally-defined options in clan-core

Darwin Support
- Services now support nix-darwin alongside NixOS
- Service authors can provide `darwinModule` in addition to `nixosModule` in their service definitions
- Wireguard service now fully supports darwin machines using wg-quick interfaces
- Added `clan.core.networking.extraHosts` for managing /etc/hosts on darwin via launchd

## Breaking Changes

Exports
- **Experimental** exports system has been redesigned.
  - Previous export definitions are no longer compatible
  - **Migration required**: Update your modules to use the standardized export options

## Misc
