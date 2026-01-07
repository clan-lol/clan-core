## Usage

```nix
inventory.instances = {
  monitoring = {
    module = {
      name = "monitoring";
      input = "clan-core";
    };

    roles = {
      client = {
        # Enable monitoring for all machines in the clan.
        tags = [ "all" ];
        # Decide whether or not your server is reachable via https.
        settings.useSSL = true;
      };

      # Select one machine as the central monitoring server.
      # Hint: This is currently limited to exactly one server.
      server.machines.<machine>.settings = {
        # Optionally enable grafana for dashboards and alerts.
        grafana.enable = true;
      };
    };
  };
};
```

## Architecture Overview

```mermaid
---
  config:
    class:
      hideEmptyMembersBox: true
---
classDiagram
    namespace server {
        class `Visualization & Alerting` {<<Grafana>>}
        class `Log Storage` {<<Grafana Loki>>}
        class `Metrics Storage` {<<Grafana Mimir>>}
    }

    namespace client {
        class `Log & Metrics Collector` {<<Grafana Alloy>>}
        class `systemd services`
        class `system metrics`
    }

    `Visualization & Alerting` --> `Metrics Storage` : metrics
    `Visualization & Alerting` --> `Log Storage` : logs
    `Log Storage` <-- `Log & Metrics Collector` : logs
    `Metrics Storage` <-- `Log & Metrics Collector` : metrics
    `Log & Metrics Collector` --> `system metrics` : metrics
    `Log & Metrics Collector` --> `systemd services` : metrics & logs
```

## Roles

### Client

Clients are machines that create metrics and logs. Those are sent to the central monitoring server for storage and visualization.

### Server

Servers store metrics and logs. They also provide optional dashboards for visualization and an alerting system.
