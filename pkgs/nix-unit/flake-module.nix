{
  perSystem = { pkgs, ... }: {
    packages.nix-unit = pkgs.callPackage ./default.nix { };
  };
}
