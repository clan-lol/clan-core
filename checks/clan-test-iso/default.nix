{
  pkgs,
  lib,
  nixosLib,
  clan-core,
  ...
}:
let
  system = pkgs.stdenv.hostPlatform.system;
  qemu-common = import (pkgs.path + "/nixos/lib/qemu-common.nix") {
    inherit lib;
    inherit (pkgs) stdenv;
  };
  isAarch64 = pkgs.stdenv.hostPlatform.isAarch64;

  # aarch64 virt has no IDE controller and no default firmware;
  # use UEFI pflash + virtio-scsi CD. x86_64 can just use -cdrom.
  qemuCdromFlags =
    if isAarch64 then
      lib.concatStringsSep " " [
        "-drive if=pflash,format=raw,unit=0,readonly=on,file=${pkgs.OVMF.firmware}"
        "-drive if=pflash,format=raw,unit=1,readonly=on,file=${pkgs.OVMF.variables}"
        "-device virtio-scsi-pci,id=scsi"
        "-device scsi-cd,drive=cd0"
        # {iso_path} is interpolated in the Python f-string
        "-drive id=cd0,if=none,format=raw,media=cdrom,readonly=on,file={iso_path}"
      ]
    else
      "-boot d -cdrom {iso_path}";
in
nixosLib.runTest (
  { config, ... }:
  let
    closureInfo = pkgs.closureInfo {
      rootPaths = [
        config.clan.test.machinesCross.${system}.peer1.config.system.build.images.iso.drvPath
        config.clan.test.machinesCross.${system}.peer1.config.clan.core.image.iso.addFilesScript
        config.clan.test.machinesCross.${system}.peer1.config.sops.package
        config.clan.test.machinesCross.${system}.peer1.config.sops.package
        config.clan.test.machinesCross.${system}.peer1.config.sops.gnupg.package
        config.clan.test.systemsFile
        config.clan.test.flakeForSandbox
      ];
    };
  in
  {
    imports = [
      clan-core.modules.nixosTest.clanTest
    ];

    hostPkgs = pkgs;

    name = "clan-test-iso";

    clan.test.fromFlake = ./.;

    # No framework-managed nodes; the ISO VM is created dynamically
    nodes = lib.mkForce { };

    testScript = ''
      import os
      import shutil
      import subprocess
      import tempfile
      import time
      from nixos_test_lib.nix_setup import prepare_test_flake
      from nixos_test_lib.port import find_free_port


      # We don't have any machines to start but this is needed, as the container
      # driver only sets up the environment correctly for nix build if this
      # function es executed
      start_all()

      with tempfile.TemporaryDirectory() as temp_dir:
          flake, _ = prepare_test_flake(temp_dir, "${config.clan.test.flakeForSandbox}", "${closureInfo}")

          # generate sops keys
          print("Generating vars...")
          subprocess.run(
              ["${
                clan-core.packages.${system}.clan-cli-full
              }/bin/clan", "vars", "keygen", "--flake", str(flake), "--debug"],
              check=True,
          )

          # Test 1: Build the ISO with clan CLI (includes secret injection)
          print("Building ISO with clan CLI...")
          result = subprocess.run(
              ["${
                clan-core.packages.${system}.clan-cli-full
              }/bin/clan", "machines", "build", "peer1", "--format", "iso", "--flake", str(flake), "--debug"],
              check=True,
              stdout=subprocess.PIPE,
              text=True,
          )
          # The last non-empty line of stdout is the ISO path
          iso_path = result.stdout.strip().splitlines()[-1]
          print(f"Built ISO at: {iso_path}")
          assert os.path.exists(iso_path), f"ISO not found at {iso_path}"

          # Test 2: Boot the ISO and verify secrets via SSH
          host_port = find_free_port()

          # Prepare SSH private key
          ssh_key = os.path.join(temp_dir, "id_ed25519")
          shutil.copy("${../assets/ssh/privkey}", ssh_key)
          os.chmod(ssh_key, 0o600)

          qemu_cmd = " ".join([
              "${qemu-common.qemuBinary pkgs.qemu_test}",
              "-m", "2048",
              "-nographic",
              f"${qemuCdromFlags}",
              f"-netdev user,id=net0,hostfwd=tcp::{host_port}-:22",
              "-device virtio-net-pci,netdev=net0",
          ])

          qemu_proc = subprocess.Popen(
            qemu_cmd,
            shell=True,
          )

          ssh_cmd = [
              "${pkgs.openssh}/bin/ssh",
              "-o", "UserKnownHostsFile=/dev/null",
              "-o", "StrictHostKeyChecking=no",
              "-o", "ConnectTimeout=3",
              "-p", str(host_port),
              "-i", ssh_key,
              "root@localhost",
          ]

          # Wait for SSH to become available by trying to connect
          print(f"Waiting for SSH on host port {host_port}...")
          for i in range(300):
              ret = subprocess.run(ssh_cmd + ["true"], capture_output=True)
              if ret.returncode == 0:
                  print(f"SSH available after {i + 1} attempts")
                  break
              time.sleep(1)
          else:
              raise Exception(f"SSH never became available on port {host_port}")

          # Verify the test-generator secret is available with the expected value
          result = subprocess.run(
              ssh_cmd + ["cat /run/secrets/vars/test-generator/test-secret"],
              check=True,
              capture_output=True,
              text=True,
          )
          actual_secret = result.stdout.strip()
          assert actual_secret == "HongKong", f"Secret mismatch: got {actual_secret!r}, expected 'HongKong'"

          # Verify SSH host keys exist
          subprocess.run(
              ssh_cmd + ["test -f /etc/ssh/ssh_host_ed25519_key"],
              check=True,
          )

          print("All ISO tests passed!")

          qemu_proc.terminate()
          qemu_proc.wait()
    '';
  }
)
