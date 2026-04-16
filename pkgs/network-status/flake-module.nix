{
  perSystem =
    {
      pkgs,
      lib,
      config,
      system,
      ...
    }:
    lib.optionalAttrs (system == "x86_64-linux" || system == "aarch64-linux") {
      devShells.network-status = pkgs.callPackage ./shell.nix { };
      packages.network-status = pkgs.callPackage ./default.nix { };
      checks = config.packages.network-status.tests;
    };
}
