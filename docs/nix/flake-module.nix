{ ... }:
{
  perSystem =
    {
      self',
      pkgs,
      lib,
      config,
      ...
    }:
    {
      devShells = lib.optionalAttrs (config.packages ? clan-site) (
        let
          clan-site-pkg = config.packages.clan-site;
        in
        {
          docs = pkgs.mkShellNoCC {
            inputsFrom = [
              clan-site-pkg
            ];
            packages = [
              config.packages.clan-site-cli
            ];
            env = clan-site-pkg.devShellEnv;
            shellHook = ''
              export PRJ_ROOT=$(git rev-parse --show-toplevel)

              # Generate reference docs into the docs/site tree
              mkdir -p $PRJ_ROOT/docs/site/reference/cli
              cp -af ${self'.packages.module-docs}/services/* $PRJ_ROOT/docs/site/services/
              cp -af ${self'.packages.module-docs}/reference/* $PRJ_ROOT/docs/site/reference/
              cp -af ${self'.packages.clan-cli-docs}/* $PRJ_ROOT/docs/site/reference/cli/
              chmod -R +w $PRJ_ROOT/docs/site

              # Set up clan-site working directory
              export CLAN_SITE_DIR=$PRJ_ROOT/pkgs/clan-site
              cd $CLAN_SITE_DIR
              ${clan-site-pkg.preBuild}

              echo "Run 'clan-site' to start the live docs server"
            '';
          };
        }
      );
      packages = {
        docs-source = pkgs.callPackage ./docs-source.nix {
          inherit (self'.packages) module-docs clan-cli-docs;
        };
      }
      // lib.optionalAttrs (pkgs.stdenv.isLinux) {
        deploy-docs-v2 = pkgs.callPackage ./deploy-docs-v2.nix { docs = self'.packages.clan-site; };
      };
    };
}
