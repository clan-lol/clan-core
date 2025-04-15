{
  pkgs,
}:
{
  lib,
  ...
}:
{
  imports = [
    ({
      # For vars we need to ensure that the system so we run vars generate on
      # is in sync with the pkgs of the system
      nixpkgs.hostPlatform = lib.mkForce pkgs.system;
      nixpkgs.pkgs = lib.mkForce pkgs;
    })
  ];
}
