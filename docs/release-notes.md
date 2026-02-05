# clan-core release notes 25.11

<!-- This is not rendered yet -->

## New features

### New Monitoring Service
Clan now provides a monitoring service based on the grafana stack.
The service consists of a server and a client role.
Servers store metrics and logs.
They also provide optional dashboards for visualization and an alerting system.
Clients are machines that create metrics and logs.
Those are sent to the central monitoring server for storage and visualization.

## ncps

- Added the ncps nix proxy binary cache service.

### Exports
- Standardized exports system with centrally-defined options in clan-core

Darwin Support
- Services now support nix-darwin alongside NixOS
- Service authors can provide `darwinModule` in addition to `nixosModule` in their service definitions
- WireGuard service now fully supports darwin machines using wg-quick interfaces
- Added `clan.core.networking.extraHosts` for managing /etc/hosts on darwin via launchd

## Breaking Changes

### Monitoring Service
The old monitoring service including telegraf has been marked deprecated for a while.
The following things related to the old monitoring stack have been removed:
- the telegraf role in `inventory.instances.monitoring.roles.telegraf`
- options related to the telegraf role:
  - `inventory.instances.monitoring.roles.telegraf.tags.all.settings.allowAllInterfaces`
  - `inventory.instances.monitoring.roles.telegraf.tags.all.settings.interfaces`

### Internet Service

The `settings.host` option in the internet service now only accepts a hostname or IP address. Port and user must be specified separately using the new `settings.port` and `settings.user` options.

**Migration:**

- **Before:** `settings.host = "root@example.com:2222";`
- **After:**
  ```nix
  settings.host = "example.com";
  settings.port = 2222;
  settings.user = "root";
  ```

The `settings.port` defaults to `22` and `settings.user` defaults to `null` (which uses `root`).

### Exports
- **Experimental** exports system has been redesigned.
  - Previous export definitions are no longer compatible
  - **Migration required**: Update your modules to use the standardized export options

### Clan Password Store Backend

The `clan.core.vars.password-store.passPackage` option has been removed. The
default backend for clan password store is now `passage` (age-based encryption).

**Migration:**

- **Before:** `clan.core.vars.password-store.passPackage = pkgs.passage;`
- **After:** `clan.core.vars.password-store.passCommand = "passage";`

The new `passCommand` option specifies the command name to execute for password
store operations. The command must be available in the system PATH and needs to
be installed by the user (e.g., via `environment.systemPackages`).

The backend now defaults to passage/age, providing improved security through age
encryption. If you were explicitly setting `passPackage`, you should update your
configuration to use `passComma
## Misc


### Facts got removed

The `facts` system has been fully removed from clan-core. The automatic migration feature (`migrateFact`) is no longer available.
Since the deprecation of facts happened already a while ago, all your facts should be migrated to vars automatically by now.
If not, have a look at the [migration guide](https://docs.clan.lol/guides/migrations/migration-facts-vars/)
