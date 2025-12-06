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
            { pkgs, lib, ... }:
            {
              clan.core.vars.settings.secretStore = "password-store";

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
              # Use a tmpfiles rule to create a writable directory and copy initial tarball there
              systemd.tmpfiles.rules = [
                "d /var/lib/secret-vars 0755 root root -"
              ];

              # Copy the initial tarball to the writable location at boot
              system.activationScripts.copySecretsTarball = {
                text = ''
                  mkdir -p /var/lib/secret-vars
                  cp ${
                    pkgs.runCommand "mock-secrets-tarball" { } ''
                      mkdir -p test-secret
                      echo "test-secret-content" > test-secret/secret1
                      tar czf $out test-secret
                    ''
                  } /var/lib/secret-vars/secrets.tar.gz
                  chmod 644 /var/lib/secret-vars/secrets.tar.gz
                '';
                deps = [ "specialfs" ];
              };

              # Point the secret location to the writable path
              clan.core.vars.password-store.secretLocation = lib.mkForce "/var/lib/secret-vars";

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
              # Use findmnt to get JSON output - stacked mounts appear as array elements
              result = machine.succeed(f"findmnt -J {path} || echo '{{}}'")
              try:
                  data = json.loads(result)
                  if "filesystems" in data:
                      # Stacked mounts at the same path appear as multiple entries in the array
                      return len(data["filesystems"])
                  return 0
              except:
                  return count_mounts(machine, path)

          def create_new_tarball(machine, content):
              """Create a new secrets tarball with the given content"""
              machine.succeed("mkdir -p /tmp/new-secrets/test-secret")
              machine.succeed(f"echo '{content}' > /tmp/new-secrets/test-secret/secret1")
              machine.succeed("tar czf /var/lib/secret-vars/secrets.tar.gz -C /tmp/new-secrets test-secret")
              machine.succeed("rm -rf /tmp/new-secrets")

          start_all()
          machine.wait_for_unit("multi-user.target")

          # Check that secrets are mounted and accessible
          machine.succeed("mountpoint -q /run/secrets")
          machine.succeed("test -f /run/secrets/test-secret/secret1")
          machine.succeed("grep -q 'test-secret-content' /run/secrets/test-secret/secret1")

          # Get initial mount count
          initial_mounts = get_mount_stack_depth(machine, "/run/secrets")
          print(f"Initial mount depth at /run/secrets: {initial_mounts}")

          # Find the install-secret-tarball script
          script_path = machine.succeed("find /nix/store -name 'install-secret-tarball' -type f | head -1").strip()
          print(f"Found script at: {script_path}")

          # Simulate running the install-secret-tarball script multiple times
          # with different content each time to verify updates are deployed
          for i in range(5):
              new_content = f"updated-secret-content-{i+1}"
              print(f"Running secret installation iteration {i+1} with content: {new_content}")

              # Create a new tarball with updated content
              create_new_tarball(machine, new_content)

              # Run the installation script
              machine.succeed(
                  f"{script_path} "
                  "/var/lib/secret-vars/secrets.tar.gz /run/secrets"
              )

              # Check secrets are still accessible
              machine.succeed("test -f /run/secrets/test-secret/secret1")

              # Verify the NEW content is deployed
              actual_content = machine.succeed("cat /run/secrets/test-secret/secret1").strip()
              if actual_content != new_content:
                  raise Exception(
                      f"Secret content not updated! "
                      f"Expected: {new_content}, Got: {actual_content}"
                  )
              print(f"✓ Secret content correctly updated to: {actual_content}")

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
          print("✓ All secret updates were correctly deployed")
        '';
      };
    };
}
