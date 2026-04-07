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
      devShells.docs = pkgs.mkShellNoCC {
        packages = [
          config.packages.clan-site-cli
        ];
        env = config.packages.clan-site.devShellEnv;
        shellHook = ''
          cd ../pkgs/clan-site
          ${config.packages.clan-site.devShellHook}
          echo "Run 'clan-site' to start the live docs server"
        '';
      };
      packages = {
        generated-docs = pkgs.callPackage ./generated-docs.nix {
          inherit (self'.packages) module-docs clan-cli-docs;
        };
        deploy-docs-v2 = pkgs.callPackage ./deploy-docs-v2.nix {
          docs = self'.packages.clan-site;
        };
      };
    };
}
