{ ... }:
{
  perSystem =
    {
      self',
      pkgs,
      lib,
      ...
    }:
    {
      devShells.docs = pkgs.mkShell {
        # nativeBuildInputs = [
        #   # Run: htmlproofer --disable-external
        #   pkgs.html-proofer
        # ]
        # ++ self'.devShells.default.nativeBuildInputs
        # ++ self'.packages.docs.nativeBuildInputs;
        shellHook = ''
          ${self'.devShells.default.shellHook}
          git_root=$(git rev-parse --show-toplevel)
          cd "$git_root"

          pushd docs

          mkdir -p ./site/reference/cli
          cp -af ${self'.packages.module-docs}/services/* ./site/services/
          cp -af ${self'.packages.module-docs}/reference/* ./site/reference/
          cp -af ${self'.packages.clan-cli-docs}/* ./site/reference/cli/

          # cp -af ${self'.packages.clan-lib-openapi} ./site/openapi.json

          chmod -R +w ./site
          echo "Generated API documentation in './site/reference/' "
        '';
      };
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
