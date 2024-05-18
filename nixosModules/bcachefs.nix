{ lib, pkgs, ... }:

{
  # Enable bcachefs support
  boot.supportedFilesystems.zfs = lib.mkForce false;
  boot.kernelPackages = lib.mkOverride 0 pkgs.linuxPackages_latest;
  boot.supportedFilesystems.bcachefs = lib.mkDefault true;
  environment.systemPackages = with pkgs; [
    bcachefs-tools
    keyutils
  ];
}
