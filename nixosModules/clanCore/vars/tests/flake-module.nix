{ ... }:
{
  perSystem =
    { ... }:
    {
      clan.nixosTests.nixos-test-password-store-mounts = {

        name = "nixos-test-password-store-mounts";

        clan = {
          directory = ./.;
          test.useContainers = false;

          machines.machine =
            { pkgs, ... }:
            {
              clan.core.vars.settings.secretStore = "password-store";
              clan.core.vars.password-store.secretLocation = "/etc/secret-vars";

              # Create a test var that will be installed
              clan.core.vars.generators.test-secret = {
                files.secret1 = {
                  secret = true;
                  neededFor = "services";
                };
                script = ''
                  echo "test-secret-content" > "$out"/secret1
                '';
              };

              # Mock the secrets tarball for testing
              # Create the tarball in /etc via environment.etc so it exists at boot
              environment.etc."secret-vars/secrets.tar.gz".source = pkgs.runCommand "mock-secrets-tarball" { } ''
                mkdir -p test-secret
                echo "test-secret-content" > test-secret/secret1
                tar czf $out test-secret
              '';

              clan.core.settings.directory = ./.;
            };
        };

        testScript = ''
          import json

          def count_mounts(machine, path):
              """Count how many times a path appears in /proc/mounts"""
              result = machine.succeed(f"grep -c ' {path} ' /proc/mounts || true").strip()
              return int(result) if result else 0

          def get_mount_stack_depth(machine, path):
              """Get the number of mounts stacked at a specific mountpoint"""
              # Use findmnt to get JSON output showing the mount tree
              result = machine.succeed(f"findmnt -J {path} || echo '{{}}'")
              try:
                  data = json.loads(result)
                  if "filesystems" in data and len(data["filesystems"]) > 0:
                      # Count nested mounts in the tree
                      def count_depth(node):
                          children = node.get("children", [])
                          if not children:
                              return 1
                          return 1 + sum(count_depth(child) for child in children)
                      return count_depth(data["filesystems"][0])
                  return 0
              except:
                  return count_mounts(machine, path)

          start_all()
          machine.wait_for_unit("multi-user.target")

          # Check that secrets are mounted and accessible
          machine.succeed("mountpoint -q /run/secrets")
          machine.succeed("test -f /run/secrets/test-secret/secret1")
          machine.succeed("grep -q 'test-secret-content' /run/secrets/test-secret/secret1")

          # Get initial mount count
          initial_mounts = get_mount_stack_depth(machine, "/run/secrets")
          print(f"Initial mount depth at /run/secrets: {initial_mounts}")

          # Check which backend we're using
          service_exists = machine.succeed("systemctl list-units --all | grep -q pass-install-secrets || echo 'no-service'").strip() != 'no-service'
          print(f"Using systemd service: {service_exists}")

          # Simulate running the install-secret-tarball script multiple times
          # This would happen during system updates or secret rotations
          for i in range(5):
              print(f"Running secret installation iteration {i+1}")
              if service_exists:
                  machine.succeed("systemctl restart pass-install-secrets.service")
                  machine.wait_for_unit("pass-install-secrets.service")
              else:
                  # Manually run the installation script (activation script mode)
                  # Find the script in the system
                  script_path = machine.succeed("find /nix/store -name 'install-secret-tarball' -type f | head -1").strip()
                  print(f"Found script at: {script_path}")
                  machine.succeed(
                      f"{script_path} "
                      "/etc/secret-vars/secrets.tar.gz /run/secrets"
                  )

              # Check secrets are still accessible
              machine.succeed("test -f /run/secrets/test-secret/secret1")

              # Check mount count hasn't grown
              current_mounts = get_mount_stack_depth(machine, "/run/secrets")
              print(f"Mount depth after iteration {i+1}: {current_mounts}")

              # Mount depth should remain exactly the same
              if current_mounts != initial_mounts:
                  raise Exception(
                      f"Mount accumulation detected! "
                      f"Initial: {initial_mounts}, Current: {current_mounts} after {i+1} iterations"
                  )

          final_mounts = get_mount_stack_depth(machine, "/run/secrets")
          print(f"Final mount depth: {final_mounts}")

          # The mount count should remain stable
          if final_mounts != initial_mounts:
              raise Exception(
                  f"Mounts accumulated over multiple runs: {initial_mounts} -> {final_mounts}"
              )

          print(f"✓ Mount count stable: {initial_mounts} -> {final_mounts}")
        '';
      };
    };
}
