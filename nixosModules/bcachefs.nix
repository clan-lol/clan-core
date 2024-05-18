{ lib, pkgs, ... }:

{
  # use latest kernel we can support to get more hardware support
  boot.kernelPackages =
    lib.mkForce
      (pkgs.zfs.override { removeLinuxDRM = pkgs.hostPlatform.isAarch64; }).latestCompatibleLinuxPackages;
  boot.zfs.removeLinuxDRM = lib.mkDefault pkgs.hostPlatform.isAarch64;

  # Enable bcachefs support
  boot.supportedFilesystems.bcachefs = lib.mkDefault true;

  environment.systemPackages = with pkgs; [
    bcachefs-tools
    keyutils
  ];
}
