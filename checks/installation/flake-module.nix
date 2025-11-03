{
  config,
  self,
  lib,
  privateInputs,
  ...
}:
{

  # The purpose of this test is to ensure `clan machines install` works
  # for machines that don't have a hardware config yet.

  # If this test starts failing it could be due to the `facter.json` being out of date
  # you can get a new one by adding
  # client.fail("cat test-flake/machines/test-install-machine/facter.json >&2")
  # to the installation test.
  clan.machines = {
    test-install-machine-without-system = {
      fileSystems."/".device = lib.mkDefault "/dev/vda";
      boot.loader.grub.device = lib.mkDefault "/dev/vda";

      imports = [
        self.nixosModules.test-install-machine-without-system
      ];
    };
  }
  // (lib.listToAttrs (
    lib.map (
      system:
      lib.nameValuePair "test-install-machine-${system}" {
        imports = [
          self.nixosModules.test-install-machine-without-system
          (
            if privateInputs ? test-fixtures then
              {
                facter.reportPath = privateInputs.test-fixtures + /nixos-vm-facter-json/${system}.json;
              }
            else
              { nixpkgs.hostPlatform = system; }
          )
        ];

        fileSystems."/".device = lib.mkDefault "/dev/vda";
        boot.loader.grub.device = lib.mkDefault "/dev/vda";
      }
    ) (lib.filter (lib.hasSuffix "linux") config.systems)
  ));

  flake.nixosModules = {
    test-install-machine-without-system =
      { lib, modulesPath, ... }:
      {
        imports = [
          (modulesPath + "/testing/test-instrumentation.nix") # we need these 2 modules always to be able to run the tests
          (modulesPath + "/profiles/qemu-guest.nix")
          self.clanLib.test.minifyModule
        ];

        networking.hostName = "test-install-machine";

        environment.etc."install-successful".text = "ok";

        # Enable SSH and add authorized key for testing
        services.openssh.enable = true;
        services.openssh.settings.PasswordAuthentication = false;
        users.users.nonrootuser = {
          isNormalUser = true;
          openssh.authorizedKeys.keys = [ (builtins.readFile ../assets/ssh/pubkey) ];
          extraGroups = [ "wheel" ];
          home = "/home/nonrootuser";
          createHome = true;
        };
        users.users.root.openssh.authorizedKeys.keys = [ (builtins.readFile ../assets/ssh/pubkey) ];
        # Allow users to manage their own SSH keys
        services.openssh.authorizedKeysFiles = [
          "/root/.ssh/authorized_keys"
          "/home/%u/.ssh/authorized_keys"
          "/etc/ssh/authorized_keys.d/%u"
        ];
        security.sudo.wheelNeedsPassword = false;

        boot.consoleLogLevel = lib.mkForce 100;
        boot.kernelParams = [ "boot.shell_on_fail" ];

        # disko config
        boot.loader.grub.efiSupport = lib.mkDefault true;
        boot.loader.grub.efiInstallAsRemovable = lib.mkDefault true;
        clan.core.vars.settings.secretStore = "vm";
        clan.core.vars.generators.test = {
          files.test.neededFor = "partitioning";
          script = ''
            echo "notok" > "$out"/test
          '';
        };
        disko.devices = {
          disk = {
            main = {
              type = "disk";
              device = "/dev/vda";

              preCreateHook = ''
                test -e /run/partitioning-secrets/test/test
              '';

              content = {
                type = "gpt";
                partitions = {
                  boot = {
                    size = "1M";
                    type = "EF02"; # for grub MBR
                    priority = 1;
                  };
                  ESP = {
                    size = "512M";
                    type = "EF00";
                    content = {
                      type = "filesystem";
                      format = "vfat";
                      mountpoint = "/boot";
                      mountOptions = [ "umask=0077" ];
                    };
                  };
                  root = {
                    size = "100%";
                    content = {
                      type = "filesystem";
                      format = "ext4";
                      mountpoint = "/";
                    };
                  };
                };
              };
            };
          };
        };
      };
  };

  perSystem =
    {
      pkgs,
      ...
    }:
    {
      # On aarch64-linux, hangs on reboot with after installation:
      # vm-test-run-test-installation-> installer # [  288.002871] reboot: Restarting system
      # vm-test-run-test-installation-> server # [test-install-machine] ### Done! ###
      # vm-test-run-test-installation-> server # [test-install-machine] + step 'Done!'
      # vm-test-run-test-installation-> server # [test-install-machine] + echo '### Done! ###'
      # vm-test-run-test-installation-> server # [test-install-machine] + rm -rf /tmp/tmp.qb16EAq7hJ
      # vm-test-run-test-installation-> (finished: must succeed: clan machines install --debug --flake test-flake --yes test-install-machine --target-host root@installer --update-hardware-config nixos-facter >&2, in 154.62 seconds)
      # vm-test-run-test-installation-> target: starting vm
      # vm-test-run-test-installation-> target: QEMU running (pid 144)
      # vm-test-run-test-installation-> target: waiting for unit multi-user.target
      # vm-test-run-test-installation-> target: waiting for the VM to finish booting
      # vm-test-run-test-installation-> target: Guest root shell did not produce any data yet...
      # vm-test-run-test-installation-> target:   To debug, enter the VM and run 'systemctl status backdoor.service'.
      checks =
        let
          closureInfo = pkgs.closureInfo {
            rootPaths = [
              privateInputs.clan-core-for-checks
              self.nixosConfigurations."test-install-machine-${pkgs.stdenv.hostPlatform.system}".config.system.build.toplevel
              self.nixosConfigurations."test-install-machine-${pkgs.stdenv.hostPlatform.system}".config.system.build.initialRamdisk
              self.nixosConfigurations."test-install-machine-${pkgs.stdenv.hostPlatform.system}".config.system.build.diskoScript
              pkgs.stdenv.drvPath
              pkgs.bash.drvPath
              pkgs.buildPackages.xorg.lndir
            ]
            ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
          };
        in
        pkgs.lib.mkIf (pkgs.stdenv.isLinux && !pkgs.stdenv.isAarch64) {
          nixos-test-installation = self.clanLib.test.baseTest {
            name = "installation";
            nodes.target = (import ./test-helpers.nix { inherit lib pkgs self; }).target;
            extraPythonPackages = _p: [
              self.legacyPackages.${pkgs.system}.nixosTestLib
            ];

            testScript = ''
              import tempfile
              import os
              import subprocess
              from nixos_test_lib.ssh import setup_ssh_connection # type: ignore[import-untyped]
              from nixos_test_lib.nix_setup import prepare_test_flake # type: ignore[import-untyped]

              def create_test_machine(oldmachine, qemu_test_bin: str, **kwargs):
                  """Create a new test machine from an installed disk image"""
                  start_command = [
                      f"{qemu_test_bin}/bin/qemu-kvm",
                      "-cpu",
                      "max",
                      "-m",
                      "3048",
                      "-virtfs",
                      "local,path=/nix/store,security_model=none,mount_tag=nix-store",
                      "-drive",
                      f"file={oldmachine.state_dir}/target.qcow2,id=drive1,if=none,index=1,werror=report",
                      "-device",
                      "virtio-blk-pci,drive=drive1",
                      "-netdev",
                      "user,id=net0",
                      "-device",
                      "virtio-net-pci,netdev=net0",
                  ]
                  machine = create_machine(start_command=" ".join(start_command), **kwargs)
                  driver.machines.append(machine)
                  return machine

              target.start()

              # Set up test environment
              with tempfile.TemporaryDirectory() as temp_dir:
                  # Prepare test flake and Nix store
                  flake_dir = prepare_test_flake(
                      temp_dir,
                      "${self.checks.${pkgs.stdenv.hostPlatform.system}.clan-core-for-checks}",
                      "${closureInfo}"
                  )

                  # Set up SSH connection
                  ssh_conn = setup_ssh_connection(
                      target,
                      temp_dir,
                      "${../assets/ssh/privkey}"
                  )

                  # Run clan install from host using port forwarding
                  clan_cmd = [
                      "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "init-hardware-config",
                      "--debug",
                      "--flake", str(flake_dir),
                      "--yes", "test-install-machine-without-system",
                      "--host-key-check", "none",
                      "--target-host", f"nonrootuser@localhost:{ssh_conn.host_port}",
                      "-i", ssh_conn.ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE']
                  ]
                  subprocess.run(clan_cmd, check=True)


                  # Run clan install from host using port forwarding
                  clan_cmd = [
                      "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "install",
                      "--phases", "disko,install",
                      "--debug",
                      "--flake", str(flake_dir),
                      "--yes", "test-install-machine-without-system",
                      "--target-host", f"nonrootuser@localhost:{ssh_conn.host_port}",
                      "-i", ssh_conn.ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE'],
                      "--update-hardware-config", "nixos-facter",
                      "--no-persist-state",
                  ]

                  subprocess.run(clan_cmd, check=True)

              # Shutdown the installer machine gracefully
              try:
                  target.shutdown()
              except BrokenPipeError:
                  # qemu has already exited
                  target.connected = False

              # Create a new machine instance that boots from the installed system
              installed_machine = create_test_machine(target, "${pkgs.qemu_test}", name="after_install")
              installed_machine.start()
              installed_machine.wait_for_unit("multi-user.target")
              installed_machine.succeed("test -f /etc/install-successful")
            '';
          } { inherit pkgs self; };

          nixos-test-update-hardware-configuration = self.clanLib.test.baseTest {
            name = "update-hardware-configuration";
            nodes.target = (import ./test-helpers.nix { inherit lib pkgs self; }).target;
            extraPythonPackages = _p: [
              self.legacyPackages.${pkgs.system}.nixosTestLib
            ];

            testScript = ''
              import tempfile
              import os
              import subprocess
              from nixos_test_lib.ssh import setup_ssh_connection # type: ignore[import-untyped]
              from nixos_test_lib.nix_setup import prepare_test_flake # type: ignore[import-untyped]

              target.start()

              # Set up test environment
              with tempfile.TemporaryDirectory() as temp_dir:
                  # Prepare test flake and Nix store
                  flake_dir = prepare_test_flake(
                      temp_dir,
                      "${self.checks.${pkgs.stdenv.hostPlatform.system}.clan-core-for-checks}",
                      "${closureInfo}"
                  )

                  # Set up SSH connection
                  ssh_conn = setup_ssh_connection(
                      target,
                      temp_dir,
                      "${../assets/ssh/privkey}"
                  )

                  # Verify files don't exist initially
                  hw_config_file = os.path.join(flake_dir, "machines/test-install-machine/hardware-configuration.nix")
                  facter_file = os.path.join(flake_dir, "machines/test-install-machine/facter.json")

                  assert not os.path.exists(hw_config_file), "hardware-configuration.nix should not exist initially"
                  assert not os.path.exists(facter_file), "facter.json should not exist initially"

                  # Test facter backend
                  clan_cmd = [
                      "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "update-hardware-config",
                      "--debug",
                      "--flake", ".",
                      "--host-key-check", "none",
                      "test-install-machine-without-system",
                      "-i", ssh_conn.ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE'],
                      "--target-host", f"nonrootuser@localhost:{ssh_conn.host_port}",
                      "--yes"
                  ]

                  result = subprocess.run(clan_cmd, capture_output=True, cwd=flake_dir)
                  if result.returncode != 0:
                      print(f"Clan update-hardware-config failed: {result.stderr.decode()}")
                      raise Exception(f"Clan update-hardware-config failed with return code {result.returncode}")

                  facter_without_system_file = os.path.join(flake_dir, "machines/test-install-machine-without-system/facter.json")
                  assert os.path.exists(facter_without_system_file), "facter.json should exist after update"
                  os.remove(facter_without_system_file)

                  # Test nixos-generate-config backend
                  clan_cmd = [
                      "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "update-hardware-config",
                      "--debug",
                      "--backend", "nixos-generate-config",
                      "--host-key-check", "none",
                      "--flake", ".",
                      "test-install-machine-without-system",
                      "-i", ssh_conn.ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE'],
                      "--target-host",
                      f"nonrootuser@localhost:{ssh_conn.host_port}",
                      "--yes"
                  ]

                  result = subprocess.run(clan_cmd, capture_output=True, cwd=flake_dir)
                  if result.returncode != 0:
                      print(f"Clan update-hardware-config (nixos-generate-config) failed: {result.stderr.decode()}")
                      raise Exception(f"Clan update-hardware-config failed with return code {result.returncode}")

                  hw_config_without_system_file = os.path.join(flake_dir, "machines/test-install-machine-without-system/hardware-configuration.nix")
                  assert os.path.exists(hw_config_without_system_file), "hardware-configuration.nix should exist after update"
            '';
          } { inherit pkgs self; };

        };
    };
}
