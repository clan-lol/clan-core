{ config, pkgs, ... }:

{

  boot.initrd.systemd = {
    enable = true;
  };

  # generates host keys for the initrd ssh daemon
  clan.core.vars.generators.initrd-ssh = {
    files."id_ed25519".neededFor = "activation"; # (3)
    files."id_ed25519.pub".secret = false;
    runtimeInputs = [
      pkgs.coreutils
      pkgs.openssh
    ];
    script = ''
      ssh-keygen -t ed25519 -N "" -f $out/id_ed25519
    '';
  };

  boot.initrd.network = {
    enable = true;

    ssh = {
      enable = true;
      port = 7172;
      authorizedKeys = [
        "<My_SSH_Public_Key>" # (1)
      ];
      hostKeys = [
        config.clan.core.vars.generators.initrd-ssh.files.id_ed25519.path
      ];
    };
  };

  boot.initrd.availableKernelModules = [
    "xhci_pci"
  ];

  # Find out the required network card driver by running `nix shell nixpkgs#pciutils -c lspci -k` on the target machine
  boot.initrd.kernelModules = [ "e1000e" ]; # (2)
}
