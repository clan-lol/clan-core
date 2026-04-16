{
  perSystem =
    {
      pkgs,
      lib,
      system,
      ...
    }:
    lib.optionalAttrs (system == "x86_64-linux" || system == "aarch64-linux") {
      packages.network-status = pkgs.callPackage ./default.nix { };
    };
}
