{ ... }:
{
  perSystem =
    {
      config,
      pkgs,
      self',
      ...
    }:
    {
      devShells.vars-generator = pkgs.callPackage ./shell.nix {
        inherit (self'.packages) generate-test-vars;
      };

      packages.generate-test-vars = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (config.packages) clan-cli;
      };
    };
}
