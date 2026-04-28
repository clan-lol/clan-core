{
  self,
  lib,
  ...
}@flakeModule:
let
  importFlake =
    flakeDir:
    let
      flakeExpr = import (flakeDir + "/flake.nix");
      inputs = lib.intersectAttrs flakeExpr.inputs self.inputs;
      flake = flakeExpr.outputs (
        inputs
        // {
          self = flake // {
            outPath = flakeDir;
          };
          clan-core = self;
          systems = builtins.toFile "flake.systems.nix" ''
            [ "x86_64-linux" "aarch64-linux" ]
          '';
        }
      );
    in
    lib.throwIf (lib.pathExists (
      flakeDir + "/flake.lock"
    )) "checks/installation/ must not have a flake.lock file" flake;

  testFlake = importFlake ./.;
in
{
  perSystem =
    {
      pkgs,
      ...
    }:
    let
      clan-core-flake-filtered = self.filter {
        name = "clan-core-flake-filtered";
        include = [
          "flake.nix"
          "flake.lock"
          "checks"
          "clanServices"
          "darwinModules"
          "flakeModules"
          "lib"
          "modules"
          "nixosModules"
        ];
      };

      systemsFile = builtins.toFile "flake.systems.nix" ''[ "${pkgs.stdenv.hostPlatform.system}" ]'';

      installationFlake =
        pkgs.runCommand "installation-test-flake-${pkgs.stdenv.hostPlatform.system}"
          {
            nativeBuildInputs = [ pkgs.nix ];
          }
          ''
            cp -r ${./.} $out
            chmod +w -R $out
            export HOME=$(mktemp -d)
            nix flake lock $out \
              --extra-experimental-features 'nix-command flakes' \
              --override-input clan-core ${clan-core-flake-filtered} \
              --override-input nixpkgs ${self.inputs.nixpkgs} \
              --override-input systems 'path://${systemsFile}' \
              --override-input clan-core/nixpkgs ${self.inputs.nixpkgs} \
              --override-input clan-core/flake-parts ${self.inputs.flake-parts} \
              --override-input clan-core/treefmt-nix ${self.inputs.treefmt-nix} \
              --override-input clan-core/nix-select ${self.inputs.nix-select} \
              --override-input clan-core/data-mesher ${self.inputs.data-mesher} \
              --override-input clan-core/sops-nix ${self.inputs.sops-nix} \
              --override-input clan-core/disko ${self.inputs.disko} \
              --override-input clan-core/systems ${self.inputs.systems}
          '';

      machineFor = name: testFlake.nixosConfigurations.${name};

      hostMachine = machineFor "test-install-machine-${pkgs.stdenv.hostPlatform.system}";
      hostAgeMachine = machineFor "test-install-machine-age-${pkgs.stdenv.hostPlatform.system}";

      closureInfo = pkgs.closureInfo {
        rootPaths = [
          installationFlake
          hostMachine.config.system.build.toplevel
          hostMachine.config.system.build.initialRamdisk
          hostMachine.config.system.build.diskoScript
          # Age backend variant — ensures age-specific packages are in the store
          hostAgeMachine.config.system.build.toplevel
          pkgs.stdenv.drvPath
          pkgs.bash.drvPath
          pkgs.buildPackages.lndir
          pkgs.makeShellWrapper
          # Needed for password-store
          pkgs.shellcheck-minimal
          pkgs.move-mount-beneath
        ]
        ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs)
        ++ builtins.map (import ./facter-report.nix) (
          lib.filter (lib.hasSuffix "linux") flakeModule.config.systems
        );
      };
    in
    {
      legacyPackages.closureInfo = closureInfo;
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
          # Use nix 2.30 for clan machines install to avoid directory permission canonicalization issue
          # Nix 2.31+ (commit c38987e04) always tries to chmod directories to 0555
          # during nix copy operations, which fails with "Operation not permitted"
          # This patched clan-cli is ONLY used for 'clan machines install' command
          installTestPkgs = pkgs.extend (
            final: prev: {
              # Override nixos-anywhere to use nix 2.30 for nix copy operations
              nixos-anywhere = prev.nixos-anywhere.override {
                nix = prev.nixVersions.nix_2_30;
              };
              # Override clan-cli to use the pkgs with patched nixos-anywhere
              clan-cli-full = self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full.override {
                pkgs = final;
              };
            }
          );
          installTestClanCli = installTestPkgs.clan-cli-full;
        in
        pkgs.lib.mkIf (pkgs.stdenv.isLinux && !pkgs.stdenv.isAarch64) {
          /*
            Test: Complete Clan machine installation workflow

            This integration test validates the full end-to-end installation process for a Clan machine
            starting from a fresh system without any pre-existing hardware configuration.

            Test flow:

            1. VM Setup: Spawns a target VM running in a NixOS installer environment

            2. Hardware Detection: Executes `clan machines init-hardware-config` to:
               - Detect hardware via SSH connection to the target
               - Generate facter.json with hardware information
               - Create initial machine configuration

            3. Encryption Setup: Runs `clan vars keygen` to generate:
               - SOPS encryption keys for secret management
               - Machine-specific key material

            4. Full Installation: Executes `clan machines install` which performs:
               - Disk partitioning using disko (tests partitioning-time secrets)
               - NixOS system installation with the generated config
               - Secret deployment for both partitioning and activation phases
               - Hardware config update using nixos-facter backend

            5. Verification:
               - Gracefully shuts down the installer VM
               - Boots a new VM from the installed disk image
               - Verifies the installation succeeded by checking for /etc/install-successful

            Objectives:

            - Validates the most common deployment scenario: installing on bare metal/VMs
              without pre-existing hardware configuration files
            - Tests the integration between clan CLI, nixos-anywhere, disko, and sops
            - Ensures secrets are properly deployed at the right stages (partitioning vs activation)
            - Verifies that hardware auto-detection (facter) works correctly

            Note: Uses Nix 2.30 to work around chmod permission issues in Nix 2.31+
          */
          nixos-test-installation = self.clanLib.test.baseTest {
            name = "installation";
            nodes.target = (import ./test-helpers.nix { inherit lib pkgs self; }).target;
            extraPythonPackages = _p: [
              self.legacyPackages.${pkgs.stdenv.hostPlatform.system}.nixosTestLib
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
                  driver.machines_qemu.append(machine)
                  return machine

              target.start()

              # Set up test environment
              with tempfile.TemporaryDirectory() as temp_dir:
                  # Prepare test flake and Nix store
                  flake_dir, _ = prepare_test_flake(
                      temp_dir,
                      "${installationFlake}",
                      "${closureInfo}"
                  )

                  # Set up SSH connection
                  ssh_conn = setup_ssh_connection(
                      target,
                      temp_dir,
                      "${../assets/ssh/privkey}"
                  )

                  # Run clan init-hardware-config from host using port forwarding
                  clan_cmd = [
                      "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}/bin/clan",
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

                  # Run clan vars keygen to generate sops keys
                  print("Starting 'clan vars keygen'...")
                  clan_cmd = [
                      "${installTestClanCli}/bin/clan",
                      "vars",
                      "keygen",
                      "--debug",
                      "--flake", str(flake_dir),
                  ]
                  subprocess.run(clan_cmd, check=True)

                  # Run clan install from host using port forwarding
                  print("Starting 'clan machines install'...")
                  clan_cmd = [
                      "${installTestClanCli}/bin/clan",
                      "machines",
                      "install",
                      "--phases", "disko,install",
                      "--debug",
                      "--flake", str(flake_dir),
                      "--yes",
                      "test-install-machine-without-system",
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
              installed_machine.shutdown()
            '';
          } { inherit pkgs self; };

          # With age backend
          nixos-test-installation-age = self.clanLib.test.baseTest {
            name = "installation";

            nodes.target = {
              imports = [ (import ./test-helpers.nix { inherit lib pkgs; }).target ];
            };

            extraPythonPackages = _p: [
              self.legacyPackages.${pkgs.stdenv.hostPlatform.system}.nixosTestLib
            ];

            testScript = ''
              import tempfile
              import os
              import subprocess
              from pathlib import Path
              from nixos_test_lib.ssh import setup_ssh_connection # type: ignore[import-untyped]
              from nixos_test_lib.nix_setup import prepare_test_flake # type: ignore[import-untyped]

              # Same key pair as in pkgs/clan-cli/clan_cli/tests/age_keys.py
              age_privkey = "AGE-SECRET-KEY-1KF8E3SR3TTGL6M476SKF7EEMR4H9NF7ZWYSLJUAK8JX276JC7KUSSURKFK"

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
                  driver.machines_qemu.append(machine)
                  return machine

              target.start()

              # Set up test environment
              with tempfile.TemporaryDirectory() as temp_dir:

                  # Set up age key file
                  age_key_dir = Path(temp_dir) / ".age"
                  age_key_dir.mkdir()
                  age_key_file = age_key_dir / "key.txt"
                  age_key_file.write_text(age_privkey)
                  os.environ["AGE_KEYFILE"] = str(age_key_file)

                  # Prepare test flake and Nix store
                  flake_dir, _ = prepare_test_flake(
                      temp_dir,
                      "${installationFlake}",
                      "${closureInfo}"
                  )

                  # Set up SSH connection
                  ssh_conn = setup_ssh_connection(
                      target,
                      temp_dir,
                      "${../assets/ssh/privkey}"
                  )

                  # Run clan init-hardware-config from host using port forwarding
                  clan_cmd = [
                      "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "init-hardware-config",
                      "--debug",
                      "--flake", str(flake_dir),
                      "--yes", "test-install-machine-without-system-with-age",
                      "--host-key-check", "none",
                      "--target-host", f"nonrootuser@localhost:{ssh_conn.host_port}",
                      "-i", ssh_conn.ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE']
                  ]
                  subprocess.run(clan_cmd, check=True)

                  # No keygen needed for age backend — machine keys are auto-generated
                  # during 'clan vars generate' / 'clan machines install'

                  # Run clan install from host using port forwarding
                  print("Starting 'clan machines install'...")
                  clan_cmd = [
                      "${installTestClanCli}/bin/clan",
                      "machines",
                      "install",
                      "--phases", "disko,install",
                      "--debug",
                      "--flake", str(flake_dir),
                      "--yes",
                      "test-install-machine-without-system-with-age",
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
              installed_machine.shutdown()
            '';
          } { inherit pkgs self; };

          # With password store
          nixos-test-installation-password-store = self.clanLib.test.baseTest {
            name = "installation";

            nodes.target = {
              imports = [ (import ./test-helpers.nix { inherit lib pkgs; }).target ];
            };

            extraPythonPackages = _p: [
              self.legacyPackages.${pkgs.stdenv.hostPlatform.system}.nixosTestLib
            ];

            testScript = ''
              import tempfile
              import os
              # import shutil
              import subprocess
              from pathlib import Path
              from nixos_test_lib.ssh import setup_ssh_connection # type: ignore[import-untyped]
              from nixos_test_lib.nix_setup import prepare_test_flake # type: ignore[import-untyped]

              os.environ["PATH"] = f"""{os.environ.get("PATH")}:${pkgs.passage}/bin:${pkgs.git}/bin:${pkgs.age}/bin"""

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
                  driver.machines_qemu.append(machine)
                  return machine

              target.start()

              # Set up test environment
              with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as pass_dir:

                  password_store_dir = str(pass_dir + "/pass")
                  Path(password_store_dir).mkdir(parents=True)
                  os.environ["PASSWORD_STORE_DIR"] = password_store_dir

                  # Copied from pkgs/clan-cli/clan_cli/tests/age_keys.py
                  age_pubkey = "age1dhwqzkah943xzc34tc3dlmfayyevcmdmxzjezdgdy33euxwf59vsp3vk3c"
                  age_privkey = "AGE-SECRET-KEY-1KF8E3SR3TTGL6M476SKF7EEMR4H9NF7ZWYSLJUAK8JX276JC7KUSSURKFK"

                  age_key_dir = Path(pass_dir + "/.age")
                  age_key_dir.mkdir()
                  age_key_file = age_key_dir / "key.txt"
                  age_key_file.write_text(age_privkey)

                  # Create .age-recipients file for passage (passage uses this instead of .gpg-id)
                  Path(password_store_dir + "/.age-recipients").write_text(f"{age_pubkey}\n")

                  # Passage uses PASSAGE_DIR (not PASSWORD_STORE_DIR like pass does)
                  os.environ["PASSAGE_DIR"] = str(password_store_dir)
                  # Set the age identities file for passage
                  os.environ["PASSAGE_IDENTITIES_FILE"] = str(age_key_file)

                  # Initialize password store as a git repository
                  # ---

                  # Path(f"{password_store_dir}/.passage").mkdir(parents=True)
                  # subprocess.run(["age-keygen", "-o", f"{password_store_dir}/.passage/identities"], cwd=password_store_dir, check=True)

                  subprocess.run(["git", "init"], cwd=password_store_dir, check=True)
                  subprocess.run(
                      ["git", "config", "user.email", "test@example.com"],
                      cwd=password_store_dir,
                      check=True,
                  )
                  subprocess.run(
                      ["git", "config", "user.name", "Test User"],
                      cwd=password_store_dir,
                      check=True,
                  )

                  # --- End of password store initialization
                  ###

                  # Prepare test flake and Nix store
                  flake_dir, _ = prepare_test_flake(
                      temp_dir,
                      "${installationFlake}",
                      "${closureInfo}"
                  )

                  # Set up SSH connection
                  ssh_conn = setup_ssh_connection(
                      target,
                      temp_dir,
                      "${../assets/ssh/privkey}"
                  )

                  # Run clan init-hardware-config from host using port forwarding
                  clan_cmd = [
                      "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}/bin/clan",
                      "machines",
                      "init-hardware-config",
                      "--debug",
                      "--flake", str(flake_dir),
                      "--yes", "test-install-machine-without-system-with-password-store",
                      "--host-key-check", "none",
                      "--target-host", f"nonrootuser@localhost:{ssh_conn.host_port}",
                      "-i", ssh_conn.ssh_key,
                      "--option", "store", os.environ['CLAN_TEST_STORE']
                  ]
                  subprocess.run(clan_cmd, check=True)

                  # Run clan install from host using port forwarding
                  print("Starting 'clan machines install'...")
                  clan_cmd = [
                      "${installTestClanCli}/bin/clan",
                      "machines",
                      "install",
                      "--phases", "disko,install",
                      "--debug",
                      "--flake", str(flake_dir),
                      "--yes",
                      "test-install-machine-without-system-with-password-store",
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
              installed_machine.shutdown()
            '';
          } { inherit pkgs self; };

          nixos-test-update-hardware-configuration = self.clanLib.test.baseTest {
            name = "update-hardware-configuration";
            nodes.target = (import ./test-helpers.nix { inherit lib pkgs self; }).target;
            extraPythonPackages = _p: [
              self.legacyPackages.${pkgs.stdenv.hostPlatform.system}.nixosTestLib
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
                  flake_dir, _ = prepare_test_flake(
                      temp_dir,
                      "${installationFlake}",
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
                      "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}/bin/clan",
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
                      "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}/bin/clan",
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
