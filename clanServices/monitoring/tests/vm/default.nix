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

      machine1.wait_for_unit("loki")
      machine1.wait_for_unit("mimir")
      machine1.wait_for_unit("grafana")
    '';
}
