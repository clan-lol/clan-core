{ ... }:
{
  perSystem =
    {
      config,
      pkgs,
      ...
    }:
    {
      # devShells.vars-generator = pkgs.callPackage ./shell.nix {

      # };
      packages.generate-test-vars = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (config.packages) clan-cli;
      };
    };
}
