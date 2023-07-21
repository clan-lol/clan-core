{
  perSystem = { pkgs, ... }:
    let
      package = pkgs.callPackage ./default.nix { };
    in
    {
      # packages.${name} = package;
      checks.python-template = package.tests.check;
    };
}
