{
  self,
  lib,

  ...
}:
let
  target =
    { modulesPath, pkgs, ... }:
    {
      imports = [
        (modulesPath + "/../tests/common/auto-format-root-device.nix")
      ];
      networking.useNetworkd = true;
      services.openssh.enable = true;
      services.openssh.settings.UseDns = false;
      services.openssh.settings.PasswordAuthentication = false;
      system.nixos.variant_id = "installer";
      environment.systemPackages = [
        pkgs.nixos-facter
      ];
      # Disable cache.nixos.org to speed up tests
      nix.settings.substituters = [ ];
      nix.settings.trusted-public-keys = [ ];
      virtualisation.emptyDiskImages = [ 512 ];
      virtualisation.diskSize = 8 * 1024;
      virtualisation.rootDevice = "/dev/vdb";
      # both installer and target need to use the same diskImage
      virtualisation.diskImage = "./target.qcow2";
      virtualisation.memorySize = 3048;
      users.users.nonrootuser = {
        isNormalUser = true;
        openssh.authorizedKeys.keys = [ (builtins.readFile ../assets/ssh/pubkey) ];
        extraGroups = [ "wheel" ];
      };
      users.users.root.openssh.authorizedKeys.keys = [ (builtins.readFile ../assets/ssh/pubkey) ];
      # Allow users to manage their own SSH keys
      services.openssh.authorizedKeysFiles = [
        "/root/.ssh/authorized_keys"
        "/home/%u/.ssh/authorized_keys"
        "/etc/ssh/authorized_keys.d/%u"
      ];
      security.sudo.wheelNeedsPassword = false;
    };
in
{

  # The purpose of this test is to ensure `clan machines install` works
  # for machines that don't have a hardware config yet.

  # If this test starts failing it could be due to the `facter.json` being out of date
  # you can get a new one by adding
  # client.fail("cat test-flake/machines/test-install-machine/facter.json >&2")
  # to the installation test.
  clan.machines.test-install-machine-without-system = {
    fileSystems."/".device = lib.mkDefault "/dev/vda";
    boot.loader.grub.device = lib.mkDefault "/dev/vda";

    imports = [ self.nixosModules.test-install-machine-without-system ];
  };
  clan.machines.test-install-machine-with-system =
    { pkgs, ... }:
    {
      # https://git.clan.lol/clan/test-fixtures
      facter.reportPath = builtins.fetchurl {
        url = "https://git.clan.lol/clan/test-fixtures/raw/commit/4a2bc56d886578124b05060d3fb7eddc38c019f8/nixos-vm-facter-json/${pkgs.hostPlatform.system}.json";
        sha256 =
          {
            aarch64-linux = "sha256:1rlfymk03rmfkm2qgrc8l5kj5i20srx79n1y1h4nzlpwaz0j7hh2";
            x86_64-linux = "sha256:16myh0ll2gdwsiwkjw5ba4dl23ppwbsanxx214863j7nvzx42pws";
          }
          .${pkgs.hostPlatform.system};
      };

      fileSystems."/".device = lib.mkDefault "/dev/vda";
      boot.loader.grub.device = lib.mkDefault "/dev/vda";

      imports = [ self.nixosModules.test-install-machine-without-system ];
    };
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
          # Custom Python package for port management utilities
          portUtils = pkgs.python3Packages.buildPythonPackage {
            pname = "port-utils";
            version = "1.0.0";
            format = "other";
            src = lib.fileset.toSource {
              root = ./.;
              fileset = ./port_utils.py;
            };
            dontUnpack = true;
            installPhase = ''
              install -D $src/port_utils.py $out/${pkgs.python3.sitePackages}/port_utils.py
              touch $out/${pkgs.python3.sitePackages}/py.typed
            '';
            doCheck = false;
          };
          closureInfo = pkgs.closureInfo {
            rootPaths = [
              self.checks.x86_64-linux.clan-core-for-checks
              self.clanInternals.machines.${pkgs.hostPlatform.system}.test-install-machine-with-system.config.system.build.toplevel
              self.clanInternals.machines.${pkgs.hostPlatform.system}.test-install-machine-with-system.config.system.build.initialRamdisk
              self.clanInternals.machines.${pkgs.hostPlatform.system}.test-install-machine-with-system.config.system.build.diskoScript
              pkgs.stdenv.drvPath
              pkgs.bash.drvPath
              pkgs.buildPackages.xorg.lndir
            ] ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs);
          };
        in
        pkgs.lib.mkIf (pkgs.stdenv.isLinux && !pkgs.stdenv.isAarch64) {
          nixos-test-installation = self.clanLib.test.baseTest {
            name = "installation";
            nodes.target = target;
            extraPythonPackages = _p: [
              portUtils
              self.legacyPackages.${pkgs.system}.setupNixInNixPythonPackage
            ];

            testScript = ''
              import tempfile
              import os
              import subprocess
              from port_utils import find_free_port, setup_port_forwarding # type: ignore[import-untyped]
              from setup_nix_in_nix import setup_nix_in_nix # type: ignore[import-untyped]

              def create_test_machine(oldmachine=None, **kwargs):
                  """Create a new test machine from an installed disk image"""
                  start_command = [
                      "${pkgs.qemu_test}/bin/qemu-kvm",
                      "-cpu", "max",
                      "-m", "3048",
                      "-virtfs", "local,path=/nix/store,security_model=none,mount_tag=nix-store",
                      "-drive", f"file={oldmachine.state_dir}/target.qcow2,id=drive1,if=none,index=1,werror=report",
                      "-device", "virtio-blk-pci,drive=drive1",
                      "-netdev", "user,id=net0",
                      "-device", "virtio-net-pci,netdev=net0",
                  ]
                  machine = create_machine(start_command=" ".join(start_command), **kwargs)
                  driver.machines.append(machine)
                  return machine

              if "NIX_REMOTE" in os.environ:
                    del os.environ["NIX_REMOTE"]  # we don't have any nix daemon running
              target.start()

              # Set up SSH key on host (test driver environment)
              with tempfile.TemporaryDirectory() as temp_dir:

                  # Set up nix chroot store environment
                  os.environ["closureInfo"] = "${closureInfo}"
                  os.environ["TMPDIR"] = temp_dir
                  
                  # Run setup function
                  setup_nix_in_nix()


                  host_port = find_free_port()
                  target.wait_for_unit("sshd.service")
                  target.wait_for_open_port(22)

                  setup_port_forwarding(target, host_port)

                  ssh_key = os.path.join(temp_dir, "id_ed25519")
                  with open(ssh_key, "w") as f:
                      with open("${../assets/ssh/privkey}", "r") as src:
                          f.write(src.read())
                  os.chmod(ssh_key, 0o600)

                  # Copy test flake to temp directory
                  flake_dir = os.path.join(temp_dir, "test-flake")
                  subprocess.run(["cp", "-r", "${self.checks.x86_64-linux.clan-core-for-checks}", flake_dir], check=True)
                  subprocess.run(["chmod", "-R", "+w", flake_dir], check=True)

                  # Run clan install from host using port forwarding
                  clan_cmd = [
                      "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "install",
                      "--phases", "disko,install",
                      "--debug",
                      "--flake", env.flake_dir,
                      "--yes", "test-install-machine-without-system",
                      "--target-host", f"nonrootuser@localhost:{host_port}",
                      "-i", ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE'],
                      "--update-hardware-config", "nixos-facter",
                  ]

                  # Set NIX_CONFIG to disable cache.nixos.org for speed
                  env = os.environ.copy()
                  env["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "
                  subprocess.run(clan_cmd, check=True, env=env)

              # Shutdown the installer machine gracefully
              try:
                  target.shutdown()
              except BrokenPipeError:
                  # qemu has already exited
                  pass

              # Create a new machine instance that boots from the installed system
              installed_machine = create_test_machine(oldmachine=target, name="after_install")
              installed_machine.start()
              installed_machine.wait_for_unit("multi-user.target")
              installed_machine.succeed("test -f /etc/install-successful")
            '';
          } { inherit pkgs self; };

          nixos-test-update-hardware-configuration = self.clanLib.test.baseTest {
            name = "update-hardware-configuration";
            nodes.target = target;
            extraPythonPackages = _p: [
              portUtils
              self.legacyPackages.${pkgs.system}.setupNixInNixPythonPackage
            ];

            testScript = ''
              import tempfile
              import os
              import subprocess
              from port_utils import find_free_port, setup_port_forwarding # type: ignore[import-untyped]
              from setup_nix_in_nix import setup_nix_in_nix # type: ignore[import-untyped]

              # Keep reference to closureInfo: ${closureInfo}

              # Set up nix chroot store environment
              os.environ["closureInfo"] = "${closureInfo}"

              # Run setup function
              setup_nix_in_nix()

              host_port = find_free_port()

              target.start()

              setup_port_forwarding(target, host_port)

              # Set up SSH key and flake on host
              with tempfile.TemporaryDirectory() as temp_dir:
                  ssh_key = os.path.join(temp_dir, "id_ed25519")
                  with open(ssh_key, "w") as f:
                      with open("${../assets/ssh/privkey}", "r") as src:
                          f.write(src.read())
                  os.chmod(ssh_key, 0o600)

                  flake_dir = os.path.join(temp_dir, "test-flake")
                  subprocess.run(["cp", "-r", "${self.checks.x86_64-linux.clan-core-for-checks}", flake_dir], check=True)
                  subprocess.run(["chmod", "-R", "+w", flake_dir], check=True)

                  # Verify files don't exist initially
                  hw_config_file = os.path.join(flake_dir, "machines/test-install-machine/hardware-configuration.nix")
                  facter_file = os.path.join(flake_dir, "machines/test-install-machine/facter.json")

                  assert not os.path.exists(hw_config_file), "hardware-configuration.nix should not exist initially"
                  assert not os.path.exists(facter_file), "facter.json should not exist initially"

                  target.wait_for_unit("sshd.service")
                  target.wait_for_open_port(22)

                  # Test facter backend
                  clan_cmd = [
                      "${self.packages.${pkgs.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "update-hardware-config",
                      "--debug",
                      "--flake", ".",
                      "--host-key-check", "none",
                      "test-install-machine-without-system",
                      "-i", ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE'],
                      f"nonrootuser@localhost:{env.host_port}"
                  ]

                  env = os.environ.copy()
                  env["CLAN_FLAKE"] = flake_dir
                  # Set NIX_CONFIG to disable cache.nixos.org for speed
                  env["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "
                  result = subprocess.run(clan_cmd, capture_output=True, cwd=flake_dir, env=env)
                  if result.returncode != 0:
                      print(f"Clan update-hardware-config failed: {result.stderr.decode()}")
                      raise Exception(f"Clan update-hardware-config failed with return code {result.returncode}")

                  facter_without_system_file = os.path.join(env.flake_dir, "machines/test-install-machine-without-system/facter.json")
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
                      "--option", "ssh-option", f"-i {ssh_key} -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/dev/null",
                      "--option", "store", os.environ['CLAN_TEST_STORE'],
                      f"nonrootuser@localhost:{env.host_port}"
                  ]

                  env = os.environ.copy()
                  env["CLAN_FLAKE"] = flake_dir
                  # Set NIX_CONFIG to disable cache.nixos.org for speed
                  env["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "
                  result = subprocess.run(clan_cmd, capture_output=True, cwd=flake_dir, env=env)
                  if result.returncode != 0:
                      print(f"Clan update-hardware-config (nixos-generate-config) failed: {result.stderr.decode()}")
                      raise Exception(f"Clan update-hardware-config failed with return code {result.returncode}")

                  hw_config_without_system_file = os.path.join(env.flake_dir, "machines/test-install-machine-without-system/hardware-configuration.nix")
                  assert os.path.exists(hw_config_without_system_file), "hardware-configuration.nix should exist after update"
            '';
          } { inherit pkgs self; };

        };
    };
}
