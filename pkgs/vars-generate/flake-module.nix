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
      packages.vars-generator = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (config.packages) clan-cli;
      };
    };
}
