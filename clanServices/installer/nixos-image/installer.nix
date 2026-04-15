{
  config,
  modulesPath,
  pkgs,
  ...
}:
{
  imports = [
    (modulesPath + "/profiles/installation-device.nix")
    ./latest-zfs-kernel.nix
  ];

  # We are stateless, so just default to latest.
  system.stateVersion = config.system.nixos.release;

  # use latest kernel we can support to get more hardware support
  boot.zfs.package = pkgs.zfs_unstable;

  documentation.man.man-db.enable = false;

  # make it easier to debug boot failures
  boot.initrd.systemd.emergencyAccess = true;

  environment.systemPackages = [
    pkgs.nixos-install-tools
    # for copying extra files of nixos-anywhere
    pkgs.rsync
    pkgs.disko
    # nixos facter is already installed through clanCore/defaults.nix:57
  ];

  # enable zswap to help with low memory systems
  boot.kernelParams = [
    "zswap.enabled=1"
    "zswap.max_pool_percent=50"
    "zswap.compressor=zstd"
    # recommended for systems with little memory
    "zswap.zpool=zsmalloc"
  ];

  # Don't add nixpkgs to the image to save space, for our intended use case we don't need it
  system.installer.channel.enable = false;
}
