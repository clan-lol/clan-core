{
  name = "monitoring";

  clan = {
    directory = ./.;
    test.useContainers = true;
    inventory = {
      machines = {
        machine1 = { };
        machine2 = { };
      };

      instances.monitoring = {
        module = {
          name = "monitoring";
          input = "self";
        };

        roles = {
          client = {
            tags.all = { };
            settings.useSSL = false;
          };
          server.machines.machine1.settings.grafana.enable = true;
        };
      };
    };
  };

  nodes = {
    machine1 = {
      networking.domain = "clan";
    };

    machine2.environment.etc."alloy/local-extension.alloy".text = ''
      // Additional machine-local Alloy config fragment.
    '';
  };

  testScript =
    { ... }:
    ''
      start_all()

      # Wait for both machines to be ready
      machine1.wait_for_unit("multi-user.target")
      machine2.wait_for_unit("multi-user.target")

      machine1.wait_for_unit("alloy")
      machine2.wait_for_unit("alloy")

      machine1.succeed("test -f /etc/alloy/config.alloy")
      machine2.succeed("test -f /etc/alloy/config.alloy")
      machine2.succeed("test -f /etc/alloy/local-extension.alloy")
      machine1.succeed("systemctl show alloy --property=ExecStart | grep -F '/etc/alloy'")
      machine2.succeed("systemctl show alloy --property=ExecStart | grep -F '/etc/alloy'")

      machine1.wait_for_unit("loki")
      machine1.wait_for_unit("mimir")
      machine1.wait_for_unit("grafana")

      config_path = machine2.succeed(
          "systemctl cat alloy | grep -o '/nix/store/[^ ]*-config.alloy'"
      ).strip()
      machine2.succeed(f"test \"$(grep -c '^loki.source.journal ' {config_path})\" = 1")
    '';
}
