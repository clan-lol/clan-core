{ self, ... }: {
  perSystem = { self', pkgs, ... }:
    let
      name = "python-template";
    in
    {
      packages.${name} = pkgs.callPackage ./default.nix { };

      devShells.${name} = pkgs.callPackage ./shell.nix {
        inherit self;
        package = (self'.packages.${name});
      };

      checks.python-template = self'.packages.${name}.tests.check;
    };
}
