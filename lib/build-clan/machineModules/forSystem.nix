{
  pkgs,
  pkgsForSystem,
  system,
}:
{
  lib,
  ...
}:
{
  imports = [
    (
      {
        # For vars we need to override the system so we run vars
        # generators on the machine that runs `clan vars generate`. If a
        # users is using the `pkgsForSystem`, we don't set
        # nixpkgs.hostPlatform it would conflict with the `nixpkgs.pkgs`
        # option.
        nixpkgs.hostPlatform = lib.mkIf (system != null && (pkgsForSystem system) != null) (
          lib.mkForce system
        );
      }
      // lib.optionalAttrs (pkgs != null) { nixpkgs.pkgs = lib.mkForce pkgs; }
    )
  ];
}
