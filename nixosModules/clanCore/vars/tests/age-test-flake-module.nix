{ ... }:
{
  perSystem =
    { ... }:
    {
      clan.nixosTests.nixos-test-age-backend = {

        name = "nixos-test-age-backend";

        clan = {
          directory = ./.;
          test.useContainers = false;

          machines.machine =
            { lib, pkgs, ... }:
            let
              # Pre-generated fixture: machine private key.
              # Encrypted .age files are in secrets/clan-vars/ (referenced via
              # settings.directory) and included in the nix store automatically.
              fixtures = ./age-fixtures;
            in
            {
              clan.core.vars.settings.secretStore = "age";
              clan.core.vars.enableConsistencyCheck = false;
              clan.core.vars.age.secretLocation = lib.mkForce "/etc/secret-vars";
              clan.core.settings.directory = lib.mkForce ./.;

              # ── Generator declarations ──────────────────────────
              # These tell age.nix what activation scripts to create
              # and where decrypted secrets should appear.
              clan.core.vars.generators.test-generator = {
                files.service-secret = {
                  secret = true;
                  neededFor = "services";
                };
                files.user-secret = {
                  secret = true;
                  neededFor = "users";
                };
                files.activation-secret = {
                  secret = true;
                  neededFor = "activation";
                };
                script = ''
                  echo -n placeholder > "$out"/service-secret
                  echo -n placeholder > "$out"/user-secret
                  echo -n placeholder > "$out"/activation-secret
                '';
              };
              clan.core.vars.generators.shared-generator = {
                share = true;
                files.shared-secret = {
                  secret = true;
                  neededFor = "services";
                };
                script = ''
                  echo -n placeholder > "$out"/shared-secret
                '';
              };
              clan.core.vars.generators.perm-generator = {
                files.perm-secret = {
                  secret = true;
                  neededFor = "services";
                  owner = "nobody";
                  group = "nogroup";
                  mode = "0440";
                };
                script = ''
                  echo -n placeholder > "$out"/perm-secret
                '';
              };

              # ── Simulate upload: place machine key + activation secrets ──
              # In production, `clan machines update` uploads the machine key
              # and pre-decrypted activation secrets via SSH.
              # Encrypted .age files come from the nix store (via settings.directory).
              system.activationScripts.mockAgeUpload = {
                text = ''
                  mkdir -p /etc/secret-vars
                  cp ${fixtures}/key.txt /etc/secret-vars/key.txt
                  chmod 600 /etc/secret-vars/key.txt

                  # Simulate activation secrets uploaded as plaintext by the deployer
                  mkdir -p /etc/secret-vars/activation/test-generator
                  ${pkgs.age}/bin/age --decrypt -i /etc/secret-vars/key.txt \
                    -o /etc/secret-vars/activation/test-generator/activation-secret \
                    ${./secrets/clan-vars/per-machine/machine/test-generator/activation-secret/activation-secret.age}
                  chmod 400 /etc/secret-vars/activation/test-generator/activation-secret
                '';
                deps = [ "specialfs" ];
              };

              # Ensure age.nix activation scripts run after our mock upload
              system.activationScripts.setupSecrets.deps = [ "mockAgeUpload" ];
              system.activationScripts.setupUserSecrets.deps = [ "mockAgeUpload" ];
            };
        };

        testScript = ''
          start_all()
          machine.wait_for_unit("multi-user.target")

          # ── Test 1: Activation scripts ran and created ramfs mounts ──
          machine.succeed("mountpoint -q /run/secrets")
          print("✓ /run/secrets is a mountpoint")

          machine.succeed("mountpoint -q /run/user-secrets")
          print("✓ /run/user-secrets is a mountpoint")

          mount_type = machine.succeed("findmnt -n -o FSTYPE /run/secrets").strip()
          assert mount_type == "ramfs", f"Expected ramfs, got '{mount_type}'"
          print("✓ /run/secrets is ramfs")

          mount_type = machine.succeed("findmnt -n -o FSTYPE /run/user-secrets").strip()
          assert mount_type == "ramfs", f"Expected ramfs, got '{mount_type}'"
          print("✓ /run/user-secrets is ramfs")

          # ── Test 2: Service secrets decrypted at boot ───────────────
          result = machine.succeed("cat /run/secrets/test-generator/service-secret").strip()
          assert result == "per-machine-service-secret", f"service-secret: expected 'per-machine-service-secret', got '{result}'"
          print("✓ Service secret decrypted on boot")

          result = machine.succeed("cat /run/secrets/shared-generator/shared-secret").strip()
          assert result == "shared-secret-content", f"shared-secret: expected 'shared-secret-content', got '{result}'"
          print("✓ Shared service secret decrypted on boot")

          # ── Test 3: User secrets decrypted before user creation ─────
          result = machine.succeed("cat /run/user-secrets/test-generator/user-secret").strip()
          assert result == "per-machine-user-secret", f"user-secret: expected 'per-machine-user-secret', got '{result}'"
          print("✓ User secret decrypted on boot")

          # ── Test 4: Activation secrets available (uploaded as plaintext) ─
          result = machine.succeed("cat /etc/secret-vars/activation/test-generator/activation-secret").strip()
          assert result == "activation-secret-content", f"activation-secret: expected 'activation-secret-content', got '{result}'"
          print("✓ Activation secret available (uploaded plaintext)")

          # ── Test 5: Permissions applied ─────────────────────────────
          stat_result = machine.succeed("stat -c '%U:%G' /run/secrets/perm-generator/perm-secret").strip()
          assert stat_result == "nobody:nogroup", f"perm-secret owner: expected 'nobody:nogroup', got '{stat_result}'"
          print("✓ Custom owner/group applied")

          mode_result = machine.succeed("stat -c '%a' /run/secrets/perm-generator/perm-secret").strip()
          assert mode_result == "440", f"perm-secret mode: expected '440', got '{mode_result}'"
          print("✓ Custom mode 0440 applied")

          default_mode = machine.succeed("stat -c '%a' /run/secrets/test-generator/service-secret").strip()
          assert default_mode == "400", f"service-secret mode: expected '400', got '{default_mode}'"
          print("✓ Default mode 0400 applied")

          # ── Test 6: Machine key exists but is protected ─────────────
          mode = machine.succeed("stat -c '%a' /etc/secret-vars/key.txt").strip()
          assert mode == "600", f"key.txt mode: expected '600', got '{mode}'"
          print("✓ Machine key has mode 0600")

          print("")
          print("═══════════════════════════════════════════════════")
          print("  NixOS age backend integration tests passed!")
          print("  Tested: activation scripts, boot ordering,")
          print("  ramfs, permissions, all secret phases")
          print("═══════════════════════════════════════════════════")
        '';
      };
    };
}
