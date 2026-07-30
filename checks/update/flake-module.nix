{
  self,
  lib,
  ...
}@flakeModule:
{
  perSystem =
    {
      pkgs,
      ...
    }:
    {
      checks =
        pkgs.lib.optionalAttrs (pkgs.stdenv.isLinux && pkgs.stdenv.hostPlatform.system == "x86_64-linux")
          {
            clan-test-update =
              let
                clan-core = self;
                nixosLib = import (self.inputs.nixpkgs + "/nixos/lib") { };
              in
              nixosLib.runTest (
                { config, ... }:
                let
                  closureInfo = pkgs.closureInfo {
                    rootPaths = [
                      self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full
                      config.clan.test.machinesCross.${pkgs.stdenv.hostPlatform.system}.machine.config.system.build.toplevel.drvPath
                      config.nodes.machine.system.build.toplevel.drvPath
                      pkgs.stdenv.drvPath
                      pkgs.buildPackages.lndir
                      pkgs.bubblewrap
                      pkgs.makeShellWrapper
                      pkgs.openssh.dev
                      pkgs.nix
                    ]
                    ++ builtins.map (i: i.outPath) (builtins.attrValues self.inputs)
                    ++ builtins.map (import ../installation/facter-report.nix) (
                      lib.filter (lib.hasSuffix "linux") flakeModule.config.systems
                    );
                  };

                in
                {
                  imports = [
                    clan-core.modules.nixosTest.clanTest
                  ];
                  hostPkgs = pkgs;

                  name = "clan-test-update";

                  clan.test.fromFlake = ./.;

                  nodes.machine.virtualisation.additionalPaths = [ closureInfo ];
                  # Needs a writable in-VM nix store with a nix database for
                  # `clan machines update` and `nix copy`
                  clan.test.useContainers = false;

                  testScript =
                    let
                      testDeps = lib.makeBinPath [
                        pkgs.age
                        pkgs.nix
                        pkgs.openssh
                        pkgs.rsync
                        pkgs.nix-diff
                        self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full
                      ];
                    in
                    ''
                      import tempfile
                      import os
                      import subprocess
                      from pathlib import Path
                      from nixos_test_lib.nix_setup import prepare_test_flake # type: ignore[import-untyped]

                      os.environ["PATH"] = "${testDeps}:" + os.environ.get("PATH", "")

                      start_all()
                      machine.wait_for_unit("multi-user.target")

                      # Verify initial state
                      machine.succeed("test -f /etc/install-successful")
                      machine.fail("test -f /etc/update-successful")

                      # Set up test environment
                      with tempfile.TemporaryDirectory() as temp_dir:
                          # Prepare test flake and Nix store
                          flake_dir, store_dir = prepare_test_flake(
                              temp_dir,
                              "${config.clan.test.flakeForSandbox}",
                              "${closureInfo}"
                          )
                          (flake_dir / ".clan-flake").write_text("")  # Ensure .clan-flake exists

                          # Generate passage identity for the test driver (needed for clan vars keygen)
                          passage_dir = Path(temp_dir) / ".passage"
                          passage_dir.mkdir(parents=True, exist_ok=True)
                          subprocess.run(["age-keygen", "-o", str(passage_dir / "identities")], check=True)
                          os.environ["HOME"] = temp_dir

                          machine.wait_for_open_port(22)
                          ssh_port = 2222
                          ssh_key = Path(temp_dir) / "id_ed25519"
                          ssh_key.write_text(Path("${../assets/ssh/privkey}").read_text())
                          ssh_key.chmod(0o600)

                          # Update the machine configuration to add a new file
                          machine_config_path = os.path.join(flake_dir, "machines", "machine", "configuration.nix")
                          os.makedirs(os.path.dirname(machine_config_path), exist_ok=True)

                          # Note: update command doesn't accept -i flag, SSH key must be in ssh-agent
                          # Start ssh-agent and add the key
                          agent_output = subprocess.check_output(["ssh-agent", "-s"], text=True)
                          for line in agent_output.splitlines():
                              if line.startswith("SSH_AUTH_SOCK="):
                                  os.environ["SSH_AUTH_SOCK"] = line.split("=", 1)[1].split(";")[0]
                              elif line.startswith("SSH_AGENT_PID="):
                                  os.environ["SSH_AGENT_PID"] = line.split("=", 1)[1].split(";")[0]

                          # Add the SSH key to the agent
                          subprocess.run(["ssh-add", str(ssh_key)], check=True)

                          print("TEST: update with --build-host local")
                          with open(machine_config_path, "w") as f:
                              f.write("""
                          {
                            environment.etc."update-build-local-successful".text = "ok";
                          }
                          """)

                          # rsync the flake into the VM. The QEMU guest is only
                          # reachable from the test driver through the forwarded
                          # SSH port on localhost; the 192.168.1.x vlan is
                          # VM-to-VM only.
                          subprocess.run(
                            [
                                "rsync",
                                "-a",
                                "--delete",
                                "-e",
                                f"ssh -p {ssh_port} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no",
                                f"{str(flake_dir)}/",
                                "root@localhost:/flake",
                            ],
                            check=True
                          )

                          # allow machine to ssh into itself
                          subprocess.run([
                              "ssh",
                              "-p", str(ssh_port),
                              "-o", "UserKnownHostsFile=/dev/null",
                              "-o", "StrictHostKeyChecking=no",
                              "root@localhost",
                              "mkdir -p /root/.ssh && chmod 700 /root/.ssh && echo \"$(cat \"${../assets/ssh/privkey}\")\" > /root/.ssh/id_ed25519 && chmod 600 /root/.ssh/id_ed25519",
                          ], check=True)

                          # install the clan-cli package into the VM's Nix store
                          subprocess.run(
                            [
                                "nix",
                                "copy",
                                "--from",
                                f"{store_dir}",
                                "--to",
                                "ssh://root@localhost",
                                "--no-check-sigs",
                                "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}",
                                "--extra-experimental-features", "nix-command flakes",
                            ],
                            check=True,
                            env={
                              **os.environ,
                              "NIX_SSHOPTS": f"-p {ssh_port} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no",
                            },
                          )

                          # generate passage identity for password-store on remote
                          subprocess.run([
                              "ssh",
                              "-p", str(ssh_port),
                              "-o", "UserKnownHostsFile=/dev/null",
                              "-o", "StrictHostKeyChecking=no",
                              "root@localhost",
                              "mkdir -p /root/.passage && ${pkgs.age}/bin/age-keygen -o /root/.passage/identities",
                          ], check=True)

                          # generate sops keys
                          subprocess.run([
                              "ssh",
                              "-p", str(ssh_port),
                              "-o", "UserKnownHostsFile=/dev/null",
                              "-o", "StrictHostKeyChecking=no",
                              "root@localhost",
                              "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}/bin/clan",
                              "vars",
                              "keygen",
                              "--flake", "/flake",
                          ], check=True)

                          # Run ssh on the host to run the clan update command via --build-host local
                          subprocess.run([
                              "ssh",
                              "-p", str(ssh_port),
                              "-o", "UserKnownHostsFile=/dev/null",
                              "-o", "StrictHostKeyChecking=no",
                              "root@localhost",
                              "${self.packages.${pkgs.stdenv.hostPlatform.system}.clan-cli-full}/bin/clan",
                              "machines",
                              "update",
                              "--debug",
                              "--flake", "/flake",
                              "--host-key-check", "none",
                              "--upload-inputs",  # Use local store instead of fetching from network
                              "--build-host", "localhost",
                              "machine",
                              "--target-host", "root@localhost",
                          ], check=True)

                          # Verify the update was successful
                          machine.succeed("test -f /etc/update-build-local-successful")


                          print("TEST: update with --target-host")

                          with open(machine_config_path, "w") as f:
                              f.write("""
                          {
                            environment.etc."target-host-update-successful".text = "ok";
                          }
                          """)

                          # Generate sops keys
                          subprocess.run([
                              "clan",
                              "vars",
                              "keygen",
                              "--flake", flake_dir,
                          ], check=True)

                          # Run clan update command
                          cmd: list[str] = [
                              "clan",
                              "machines",
                              "update",
                              "--debug",
                              "--flake", str(flake_dir),
                              "--host-key-check", "none",
                              "--upload-inputs",  # Use local store instead of fetching from network
                              "machine",
                              "--target-host", f"root@localhost:{ssh_port}",
                          ]
                          print("Running command:", " ".join(cmd))
                          subprocess.run(cmd, check=True)

                          # Verify the update was successful
                          machine.succeed("test -f /etc/target-host-update-successful")


                          print("TEST: update with --build-host")
                          # Update configuration again
                          with open(machine_config_path, "w") as f:
                              f.write("""
                          {
                            environment.etc."build-host-update-successful".text = "ok";
                          }
                          """)

                          # Run clan update command with --build-host
                          subprocess.run([
                              "clan",
                              "machines",
                              "update",
                              "--debug",
                              "--flake", flake_dir,
                              "--host-key-check", "none",
                              "--upload-inputs",  # Use local store instead of fetching from network
                              "--build-host", f"root@localhost:{ssh_port}",
                              "machine",
                              "--target-host", f"root@localhost:{ssh_port}",
                          ], check=True)

                          # Verify the second update was successful
                          machine.succeed("test -f /etc/build-host-update-successful")


                          print("TEST: update fails with switch inhibitors and suggests reboot")
                          # The base machine config already sets
                          # system.switch.inhibitors.test-component = "original";
                          # Deploying a different value triggers the inhibitor check.
                          with open(machine_config_path, "w") as f:
                              f.write("""
                          {lib, ...}: {
                            environment.etc."inhibitor-test-marker".text = "ok";
                            system.switch.inhibitors.test-component = lib.mkForce "changed";
                          }
                          """)

                          # Run clan update — expect failure due to inhibitors.
                          result = subprocess.run([
                              "clan",
                              "machines",
                              "update",
                              "--debug",
                              "--flake", str(flake_dir),
                              "--host-key-check", "none",
                              "--upload-inputs",
                              "machine",
                              "--target-host", f"root@localhost:{ssh_port}",
                          ], capture_output=True, text=True)
                          assert result.returncode != 0, (
                              f"Expected update to fail due to switch inhibitors, "
                              f"but it succeeded.\nstdout: {result.stdout}\nstderr: {result.stderr}"
                          )
                          combined = result.stdout + result.stderr
                          assert "reboot" in combined.lower(), (
                              f"Error should suggest reboot, got:\n{combined}"
                          )

                          # Verify: boot entry was registered despite switch failure.
                          # The profile points to the new config (boot was successful),
                          # but /run/current-system still points to the old one (switch failed).
                          # Check that the profile's switch-inhibitors file contains our value.
                          machine.succeed("grep -q test-component $(readlink -f /nix/var/nix/profiles/system)/switch-inhibitors")
                          # The marker file must NOT exist because switch was blocked.
                          machine.fail("test -f /etc/inhibitor-test-marker")


                          print("TEST: NIXOS_NO_CHECK=1 forces past switch inhibitors")
                          # The previous test left the system with test-component="original"
                          # (switch was blocked, so /run/current-system is unchanged).
                          # Same config change, but now with NIXOS_NO_CHECK=1 to force through.
                          os.environ["NIXOS_NO_CHECK"] = "1"
                          try:
                              subprocess.run([
                                  "clan",
                                  "machines",
                                  "update",
                                  "--debug",
                                  "--flake", str(flake_dir),
                                  "--host-key-check", "none",
                                  "--upload-inputs",
                                  "machine",
                                  "--target-host", f"root@localhost:{ssh_port}",
                              ], check=True)
                          finally:
                              del os.environ["NIXOS_NO_CHECK"]

                          # Now the switch succeeded — marker file must exist.
                          machine.succeed("test -f /etc/inhibitor-test-marker")
                    '';
                }
              );
          };
    };
}
