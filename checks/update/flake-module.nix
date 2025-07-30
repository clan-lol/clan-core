{ self, ... }:
{
  # Machine for update test
  clan.machines.test-update-machine = {
    imports = [
      self.nixosModules.test-update-machine
      # Import the configuration file that will be created/updated during the test
      ./test-update-machine/configuration.nix
    ];
  };
  flake.nixosModules.test-update-machine =
    { lib, modulesPath, ... }:
    {
      imports = [
        (modulesPath + "/testing/test-instrumentation.nix")
        (modulesPath + "/profiles/qemu-guest.nix")
        self.clanLib.test.minifyModule
        ../../lib/test/container-test-driver/nixos-module.nix
      ];

      # Apply patch to fix x-initrd.mount filesystem handling in switch-to-configuration-ng
      nixpkgs.overlays = [
        (_final: prev: {
          switch-to-configuration-ng = prev.switch-to-configuration-ng.overrideAttrs (old: {
            patches = (old.patches or [ ]) ++ [ ./switch-to-configuration-initrd-mount-fix.patch ];
          });
        })
      ];

      networking.hostName = "update-machine";

      environment.etc."install-successful".text = "ok";

      # Enable SSH and add authorized key for testing
      services.openssh.enable = true;
      services.openssh.settings.PasswordAuthentication = false;
      users.users.root.openssh.authorizedKeys.keys = [ (builtins.readFile ../assets/ssh/pubkey) ];
      security.sudo.wheelNeedsPassword = false;

      boot.consoleLogLevel = lib.mkForce 100;
      boot.kernelParams = [ "boot.shell_on_fail" ];

      boot.isContainer = true;
      nixpkgs.hostPlatform = lib.mkDefault "x86_64-linux";
      # Preserve the IP addresses assigned by the test framework
      # (based on virtualisation.vlans = [1] and node number 1)
      networking.interfaces.eth1 = {
        useDHCP = false;
        ipv4.addresses = [
          {
            address = "192.168.1.1";
            prefixLength = 24;
          }
        ];
        ipv6.addresses = [
          {
            address = "2001:db8:1::1";
            prefixLength = 64;
          }
        ];
      };

      # Define the mounts that exist in the container to prevent them from being stopped
      fileSystems = {
        "/" = {
          device = "/dev/disk/by-label/nixos";
          fsType = "ext4";
          options = [ "x-initrd.mount" ];
        };
        "/nix/.rw-store" = {
          device = "tmpfs";
          fsType = "tmpfs";
          options = [
            "mode=0755"
          ];
        };
        "/nix/store" = {
          device = "overlay";
          fsType = "overlay";
          options = [
            "lowerdir=/nix/.ro-store"
            "upperdir=/nix/.rw-store/upper"
            "workdir=/nix/.rw-store/work"
          ];
        };
      };
    };

  perSystem =
    {
      pkgs,
      ...
    }:
    {
      checks =
        pkgs.lib.optionalAttrs (pkgs.stdenv.isLinux && pkgs.stdenv.hostPlatform.system == "x86_64-linux")
          {
            nixos-test-update =
              let
                closureInfo = pkgs.closureInfo {
                  rootPaths = [
                    self.checks.x86_64-linux.clan-core-for-checks
                    self.clanInternals.machines.${pkgs.hostPlatform.system}.test-update-machine.config.system.build.toplevel
                    pkgs.stdenv.drvPath
                    pkgs.bash.drvPath
                    pkgs.buildPackages.xorg.lndir
                  ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
                };
              in
              self.clanLib.test.containerTest {
                name = "update";
                nodes.machine = {
                  imports = [ self.nixosModules.test-update-machine ];
                };
                extraPythonPackages = _p: [
                  self.legacyPackages.${pkgs.system}.nixosTestLib
                ];

                testScript = ''
                  import tempfile
                  import os
                  import subprocess
                  from nixos_test_lib.ssh import setup_ssh_connection # type: ignore[import-untyped]
                  from nixos_test_lib.nix_setup import prepare_test_flake # type: ignore[import-untyped]

                  start_all()
                  machine.wait_for_unit("multi-user.target")

                  # Verify initial state
                  machine.succeed("test -f /etc/install-successful")
                  machine.fail("test -f /etc/update-successful")

                  # Set up test environment
                  with tempfile.TemporaryDirectory() as temp_dir:
                      # Prepare test flake and Nix store
                      flake_dir = prepare_test_flake(
                          temp_dir,
                          "${self.checks.x86_64-linux.clan-core-for-checks}",
                          "${closureInfo}"
                      )
                      (flake_dir / ".clan-flake").write_text("")  # Ensure .clan-flake exists

                      # Set up SSH connection
                      ssh_conn = setup_ssh_connection(
                          machine,
                          temp_dir,
                          "${../assets/ssh/privkey}"
                      )

                      # Update the machine configuration to add a new file
                      machine_config_path = os.path.join(flake_dir, "machines", "test-update-machine", "configuration.nix")
                      os.makedirs(os.path.dirname(machine_config_path), exist_ok=True)
                      
                      with open(machine_config_path, "w") as f:
                          f.write("""
                      {
                        environment.etc."update-successful".text = "ok";
                      }
                      """)

                      # Run clan update command  
                      # Note: update command doesn't accept -i flag, SSH key must be in ssh-agent
                      # Start ssh-agent and add the key
                      agent_output = subprocess.check_output(["${pkgs.openssh}/bin/ssh-agent", "-s"], text=True)
                      for line in agent_output.splitlines():
                          if line.startswith("SSH_AUTH_SOCK="):
                              os.environ["SSH_AUTH_SOCK"] = line.split("=", 1)[1].split(";")[0]
                          elif line.startswith("SSH_AGENT_PID="):
                              os.environ["SSH_AGENT_PID"] = line.split("=", 1)[1].split(";")[0]
                      
                      # Add the SSH key to the agent
                      subprocess.run(["${pkgs.openssh}/bin/ssh-add", ssh_conn.ssh_key], check=True)


                      # Run clan update command
                      subprocess.run([
                          "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                          "machines",
                          "update",
                          "--debug",
                          "--flake", flake_dir,
                          "--host-key-check", "none",
                          "--fetch-local",  # Use local store instead of fetching from network
                          "test-update-machine",
                          "--target-host", f"root@192.168.1.1:{ssh_conn.host_port}",
                      ], check=True)

                      # Verify the update was successful
                      machine.succeed("test -f /etc/update-successful")

                      # Test update with --build-host
                      # Update configuration again to test build-host functionality
                      with open(machine_config_path, "w") as f:
                          f.write("""
                      {
                        environment.etc."build-host-update-successful".text = "ok";
                      }
                      """)

                      # Run clan update command with --build-host
                      subprocess.run([
                          "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                          "machines",
                          "update",
                          "--debug",
                          "--flake", flake_dir,
                          "--host-key-check", "none",
                          "--fetch-local",  # Use local store instead of fetching from network
                          "--build-host", f"root@192.168.1.1:{ssh_conn.host_port}",
                          "test-update-machine",
                          "--target-host", f"root@192.168.1.1:{ssh_conn.host_port}",
                      ], check=True)

                      # Verify the second update was successful
                      machine.succeed("test -f /etc/build-host-update-successful")

                      # Run clan update command with --build-host
                      subprocess.run([
                          "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                          "machines",
                          "update",
                          "--debug",
                          "--flake", flake_dir,
                          "--host-key-check", "none",
                          "--fetch-local",  # Use local store instead of fetching from network
                          "--build-host", f"root@192.168.1.1:{ssh_conn.host_port}",
                          "test-update-machine",
                          "--target-host", f"root@192.168.1.1:{ssh_conn.host_port}",
                      ], check=True)

                      # Verify the second update was successful
                      machine.succeed("test -f /etc/build-host-update-successful")
                '';
              } { inherit pkgs self; };
          };
    };
}
