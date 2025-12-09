# Standalone VM base module that can be imported independently
# This module contains the core VM configuration without the system extension
{
  lib,
  config,
  pkgs,
  modulesPath,
  ...
}:
let
  # Flatten the list of state folders into a single list
  stateFolders = lib.flatten (
    lib.mapAttrsToList (_item: attrs: attrs.folders) config.clan.core.state
  );
in
{
  imports = [
    (modulesPath + "/virtualisation/qemu-vm.nix")
    ./serial.nix
    ./waypipe.nix
  ];

  clan.core.state.HOME.folders = [ "/home" ];

  clan.services.waypipe = {
    inherit (config.clan.core.vm.inspect.waypipe) enable command;
  };

  # required for issuing shell commands via qga
  services.qemuGuest.enable = true;

  # required to react to system_powerdown qmp command
  # Some desktop managers like xfce override the poweroff signal and therefore
  #   make it impossible to handle it via 'logind' directly.
  services.acpid.enable = true;
  services.acpid.handlers.power.event = "button/power.*";
  services.acpid.handlers.power.action = "poweroff";

  # only works on x11
  services.spice-vdagentd.enable = config.services.xserver.enable;

  # logrotate crashes sometimes
  services.logrotate.enable = false;

  boot.initrd.systemd.enable = true;

  boot.initrd.systemd.storePaths = [
    pkgs.util-linux
    pkgs.e2fsprogs
  ];
  boot.initrd.systemd.emergencyAccess = true;

  # userborn would be faster because it doesn't need perl, but it cannot create normal users
  services.userborn.enable = true;
  users.mutableUsers = false;
  users.allowNoPasswordLogin = true;

  boot.initrd.kernelModules = [ "virtiofs" ];
  virtualisation.writableStore = false;
  virtualisation.fileSystems = lib.mkForce (
    {
      "/nix/store" = {
        device = "nix-store";
        options = [
          "x-systemd.requires=systemd-modules-load.service"
          "ro"
        ];
        fsType = "virtiofs";
      };

      "/" = {
        device = "/dev/vda";
        fsType = "ext4";
        options = [
          "defaults"
          "x-systemd.makefs"
          "nobarrier"
          "noatime"
          "nodiratime"
          "data=writeback"
          "discard"
        ];
      };

      "/vmstate" = {
        device = "/dev/vdb";
        options = [
          "x-systemd.makefs"
          "noatime"
          "nodiratime"
          "discard"
        ];
        noCheck = true;
        fsType = "ext4";
      };

      ${config.clan.core.vars.sops.secretUploadDirectory} = {
        device = "secrets";
        fsType = "9p";
        neededForBoot = true;
        options = [
          "trans=virtio"
          "version=9p2000.L"
          "cache=loose"
        ];
      };
    }
    // lib.listToAttrs (
      map (
        folder:
        lib.nameValuePair folder {
          device = "/vmstate${folder}";
          fsType = "none";
          options = [ "bind" ];
        }
      ) stateFolders
    )
  );
}
