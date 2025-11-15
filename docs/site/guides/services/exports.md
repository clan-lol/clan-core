# Service Exports

## Overview

**Exports** are a mechanism for services to share structured configuration data between machines in a multi-host service. They provide a standardized way for different machines and service instances to discover and access information they need from each other.

## Use Cases

Exports are useful when you need to:

- Share network configuration (IP addresses, ports, etc.) between service components
- Distribute generated credentials or connection strings to consuming machines
- Provide discovery information for peers in a distributed service
- Enable machines to dynamically configure themselves based on the topology of other machines

**Example scenarios:**
- A VPN service where peers need to know each other's public endpoints
- A database cluster where replicas need the primary's connection string
- A monitoring system where agents need the metrics collector's address

## How Exports Work

Exports use a **scope-based system** with four components:

```
SERVICE:INSTANCE:ROLE:MACHINE
```

Each part can be empty (represented by an empty string), meaning "all" or "global":

- **`serviceName`**: The name of the service (e.g., "zerotier", "wireguard")
- **`instanceName`**: A specific instance of that service
- **`roleName`**: A role within the service (e.g., "client", "server", "peer")
- **`machineName`**: A specific machine name

**Example scopes:**
- `"zerotier:default:peer:machine01"` - Data specific to machine01's peer role in the default zerotier instance
- `"zerotier:::"` - Global data for the zerotier service across all instances
- `":::machine01"` - Global data for machine01 across all services
- `":::"` - Truly global data

## Defining Exports in Your Service

To export data from your service, use the `mkExports` helper function available in the `perInstance` context:

```nix
{
  roles.peer = {
    perInstance = { instanceName, mkExports, roles, lib, ... }: {
      exports = mkExports {
        # Your exported data here
        networking = {
          priority = lib.mkDefault 900;
          module = "clan_lib.network.zerotier";
          peers = lib.mapAttrs (name: _machine: {
            host.var = {
              machine = name;
              generator = "zerotier";
              file = "zerotier-ip";
            };
          }) roles.peer.machines;
        };
      };

      nixosModule = { ... }: {
        # Your NixOS configuration
      };
    };
  };
}
```

The `mkExports` function automatically creates the appropriate scope key for your exports based on the current service, instance, role, and machine context.

## Accessing Exports

Within your service module, you can access exports from the `exports` parameter available in the `perInstance` context:

```nix
perInstance = { exports, instanceName, machine, ... }: {
  nixosModule = { ... }: {
    # Access global exports
    # exports.":::"

    # Access service-level exports
    # exports."myservice:::"

    # Access specific machine exports
    # exports."myservice:instance01:peer:machine02"
  };
};
```

### Export Scope Patterns

**Service-level exports** (available to all instances/machines of a service):
```nix
exports."myservice:::" = {
  apiVersion = "v1";
  clusterConfig = { ... };
};
```

**Instance-level exports** (specific to one instance):
```nix
exports."myservice:instance01::" = {
  instanceId = "abc123";
};
```

**Role+Machine exports** (specific to a role on a machine):
```nix
exports."myservice:instance01:server:backend01" = {
  ipAddress = "192.168.1.10";
  port = 5432;
};
```

## Helper Functions

The `clanLib.exports` module provides several helper functions for working with exports:

### `buildScopeKey`

Build a scope key string from components:

```nix
clanLib.exports.buildScopeKey {
  serviceName = "myservice";
  instanceName = "prod";
  roleName = "server";
  machineName = "backend01";
}
# => "myservice:prod:server:backend01"
```

### `parseScope`

Parse a scope string into its components:

```nix
clanLib.exports.parseScope "myservice:prod:server:backend01"
# => {
#   serviceName = "myservice";
#   instanceName = "prod";
#   roleName = "server";
#   machineName = "backend01";
# }
```

### `getExport`

Retrieve a single export by scope:

```nix
clanLib.exports.getExport
  { serviceName = "myservice"; machineName = "backend01"; }
  exports
# => exports."myservice:::backend01"
```

### `selectExports`

Filter exports matching specific criteria:

```nix
# Get all exports for a specific service
clanLib.exports.selectExports
  { serviceName = "myservice"; }
  exports

# Get all exports for a specific machine
clanLib.exports.selectExports
  { machineName = "backend01"; }
  exports
```

## Best Practices

1. **Use appropriate scopes**: Export at the narrowest scope that makes sense
   - Service-wide configuration → `"myservice:::"`
   - Machine-specific data → `"myservice:::machine01"`
   - Role-instance-machine data → `"myservice:inst:role:machine"`

2. **Structure your exports logically**: Group related data under descriptive keys

3. **Document your exports**: Add comments explaining what data is exported and why

4. **Avoid circular dependencies**: Be careful not to create situations where machines depend on each other's exports in a circular manner

5. **Use `lib.mkDefault` for priorities**: When exporting configuration that might be overridden, use `lib.mkDefault` to set appropriate precedence

## Complete Example

Here's a simplified example of a distributed key-value store service using exports:

```nix
{
  _class = "clan.service";
  manifest.name = "kvstore";

  roles.primary = {
    perInstance = { mkExports, ... }: {
      exports = mkExports {
        connectionString = "tcp://primary:6379";
        isLeader = true;
      };

      nixosModule = { ... }: {
        services.kvstore = {
          enable = true;
          mode = "primary";
        };
      };
    };
  };

  roles.replica = {
    perInstance = { exports, instanceName, machine, mkExports, ... }: {
      # Replicas export their own connection info
      exports = mkExports {
        connectionString = "tcp://${machine.name}:6379";
        isLeader = false;
      };

      nixosModule = { ... }: {
        services.kvstore = {
          enable = true;
          mode = "replica";
          # Access the primary's connection string from exports
          primaryEndpoint = exports."kvstore:${instanceName}:primary:".connectionString or null;
        };
      };
    };
  };
}
```

## Further Reading

- [Service Author Reference](../../reference/options/clan_service.md)
- [Introduction to clanServices](./introduction-to-services.md)
- [Authoring a clanService](./community.md)
