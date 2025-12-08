{ self, ... }:
{
  # Define machines that use the nixOS modules
  clan.machines = {
    test-vm-persistence-x86_64-linux = {
      imports = [ self.nixosModules.test-vm-persistence ];
      nixpkgs.hostPlatform = "x86_64-linux";
    };
    test-vm-persistence-aarch64-linux = {
      imports = [ self.nixosModules.test-vm-persistence ];
      nixpkgs.hostPlatform = "aarch64-linux";
    };
    test-vm-deployment-x86_64-linux = {
      imports = [ self.nixosModules.test-vm-deployment ];
      nixpkgs.hostPlatform = "x86_64-linux";
    };
    test-vm-deployment-aarch64-linux = {
      imports = [ self.nixosModules.test-vm-deployment ];
      nixpkgs.hostPlatform = "aarch64-linux";
    };
  };

  flake.nixosModules = {
    # NixOS module for test_vm_persistence
    test-vm-persistence =
      { config, lib, ... }:
      {
        imports = [ self.nixosModules.clan-vm-base ];

        system.stateVersion = config.system.nixos.release;

        # Disable system.checks to avoid rebuild mismatches in tests
        system.checks = lib.mkForce [ ];

        services.getty.autologinUser = "root";

        # Basic networking setup
        networking.useDHCP = false;
        networking.firewall.enable = false;

        # VM-specific settings
        clan.virtualisation.graphics = false;
        clan.core.networking.targetHost = "client";

        # State configuration for persistence test
        clan.core.state.my_state.folders = [
          "/var/my-state"
          "/var/user-state"
        ];

        # Initialize users for tests
        users.users = {
          root = {
            initialPassword = "root";
          };
          test = {
            initialPassword = "test";
            isSystemUser = true;
            group = "users";
          };
        };
      };

    # NixOS module for test_vm_deployment
    test-vm-deployment =
      { config, lib, ... }:
      {
        imports = [ self.nixosModules.clan-vm-base ];

        system.stateVersion = config.system.nixos.release;

        # Disable services that might cause issues in tests
        systemd.services.logrotate-checkconf.enable = false;
        services.getty.autologinUser = "root";

        # Basic networking setup
        networking.useDHCP = false;
        networking.firewall.enable = false;

        # VM-specific settings
        clan.virtualisation.graphics = false;

        # SSH for deployment tests
        services.openssh.enable = true;

        # Disable system.checks to avoid rebuild mismatches in tests
        system.checks = lib.mkForce [ ];

        # Initialize users for tests
        users.users = {
          root = {
            initialPassword = "root";
          };
        };

        # hack to make sure
        sops.validateSopsFiles = false;
        sops.secrets."vars/m1_generator/my_secret" = lib.mkDefault {
          sopsFile = builtins.toFile "fake" "";
        };

        # Vars generators configuration
        clan.core.vars.generators = {
          m1_generator = {
            files.my_secret = {
              secret = true;
              path = "/run/secrets/vars/m1_generator/my_secret";
            };
            script = ''
              echo hello > "$out"/my_secret
            '';
          };

          my_shared_generator = {
            share = true;
            files = {
              shared_secret = {
                secret = true;
                path = "/run/secrets/vars/my_shared_generator/shared_secret";
              };
              no_deploy_secret = {
                secret = true;
                deploy = false;
                path = "/run/secrets/vars/my_shared_generator/no_deploy_secret";
              };
            };
            script = ''
              echo hello > "$out"/shared_secret
              echo hello > "$out"/no_deploy_secret
            '';
          };
        };
      };
  };
}
