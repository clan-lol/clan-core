import ../lib/test-base.nix ({ config, pkgs, lib, ... }: {
  name = "wayland-proxy-virtwl";

  nodes.machine = { self, ... }: {
    imports = [
      self.nixosModules.clanCore
      {
        clanCore.machineName = "machine";
        clanCore.clanDir = ./.;
      }
    ];
    services.wayland-proxy-virtwl.enable = true;

    virtualisation.qemu.options = [
      "-vga none -device virtio-gpu-rutabaga,cross-domain=on,hostmem=4G,wsi=headless"
    ];
    virtualisation.qemu.package = lib.mkForce self.packages.${pkgs.hostPlatform.system}.qemu-wayland;
  };
  # FIXME: currently we still see this error in the build sandbox,
  # but it gives us some smoke test
  # vm-test-run-wayland-proxy-virtwl> machine # qemu-kvm: The errno is ENOENT: No such file or directory
  # vm-test-run-wayland-proxy-virtwl> machine # qemu-kvm: CHECK failed in rutabaga_cmd_submit_3d() ../hw/display/virtio-gpu-rutabaga.c:341
  # vm-test-run-wayland-proxy-virtwl> machine # qemu-kvm: virtio_gpu_rutabaga_process_cmd: ctrl 0x207, error 0x1200
  testScript = ''
    start_all()
    # use machinectl
    machine.succeed("machinectl shell .host ${config.nodes.machine.systemd.package}/bin/systemctl --user start wayland-proxy-virtwl >&2")
  '';
})
