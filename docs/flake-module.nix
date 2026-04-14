{ ... }:
{
  perSystem =
    {
      self',
      pkgs,
      config,
      ...
    }:
    {
      packages = {
        generated-docs = pkgs.callPackage ./nix/generated-docs.nix {
          inherit (self'.packages) module-docs clan-cli-docs;
        };
        deploy-docs-v2 = pkgs.callPackage ./nix/deploy-docs-v2.nix {
          docs = self'.packages.clan-site;
        };
      };
      devShells.docs = pkgs.callPackage ./nix/shell.nix {
        inherit (config.packages) clan-site clan-site-cli;
      };
    };
}
