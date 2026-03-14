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
            settings.loki.journal.relabelRules.beforeNormalization = [
              ''
                rule {
                  source_labels = ["__journal__systemd_unit"]
                  target_label = "raw_service_name"
                }
              ''
            ];
            settings.loki.journal.relabelRules.afterNormalization = [
              ''
                rule {
                  source_labels = ["level"]
                  target_label = "normalized_level"
                }
              ''
            ];
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

      machine2.succeed("test \"$(grep -c '^loki.source.journal ' /etc/alloy/config.alloy)\" = 1")
      config = machine2.succeed("cat /etc/alloy/config.alloy")

      pre_line = next(i for i, line in enumerate(config.splitlines(), 1) if 'target_label = "raw_service_name"' in line)
      instance_line = next(i for i, line in enumerate(config.splitlines(), 1) if 'target_label = "instance"' in line)
      level_line = next(i for i, line in enumerate(config.splitlines(), 1) if 'target_label = "level"' in line)
      post_line = next(i for i, line in enumerate(config.splitlines(), 1) if 'target_label = "normalized_level"' in line)

      assert pre_line < instance_line < level_line < post_line, (
          pre_line,
          instance_line,
          level_line,
          post_line,
      )
    '';
}
