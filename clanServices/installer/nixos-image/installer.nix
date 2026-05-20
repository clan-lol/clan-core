{
  options,
  config,
  lib,
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

  # Mirror upstream's default explicitly to silence the 26.05 eval warning.
  boot.zfs.forceImportRoot =
    assert lib.assertMsg (lib.versionOlder config.system.stateVersion "26.11")
      "boot.zfs.forceImportRoot override is no longer needed: upstream default is `false` for stateVersion >= 26.11. Remove this line.";
    options.boot.zfs.forceImportRoot.default;

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
