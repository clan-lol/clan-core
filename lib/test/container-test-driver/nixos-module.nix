{ pkgs, lib, ... }:
{
  boot.isContainer = true;

  # needed since nixpkgs 7fb2f407c01b017737eafc26b065d7f56434a992 removed the getty unit by default
  console.enable = true;

  # undo qemu stuff
  system.build.initialRamdisk = "";
  virtualisation.sharedDirectories = lib.mkForce { };
  networking.useDHCP = false;

  # We use networkd to assign static ip addresses
  networking.useNetworkd = true;
  services.resolved.enable = false;

  # Rename the host0 interface to eth0 to match what we expect in VM tests.
  system.activationScripts.renameInterface = ''
    ${pkgs.iproute2}/bin/ip link set dev host0 name eth1
  '';

  systemd.services.backdoor.enable = false;

  # we don't have permission to set cpu scheduler in our container
  systemd.services.nix-daemon.serviceConfig.CPUSchedulingPolicy = lib.mkForce "";
}
