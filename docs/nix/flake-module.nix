{ inputs, ... }:
{
  perSystem =
    {
      config,
      self',
      pkgs,
      ...
    }:
    {
      devShells.docs = self'.packages.docs.overrideAttrs (_old: {
        nativeBuildInputs = [
          # Run: htmlproofer --disable-external
          pkgs.html-proofer
        ]
        ++ self'.devShells.default.nativeBuildInputs
        ++ self'.packages.docs.nativeBuildInputs;
        shellHook = ''
          ${self'.devShells.default.shellHook}
          git_root=$(git rev-parse --show-toplevel)
          cd "$git_root"
          runPhase configurePhase
        '';
      });
      packages = {
        docs = pkgs.python3.pkgs.callPackage ./default.nix {
          inherit (self'.packages)
            clan-cli-docs
            option-search
            inventory-api-docs
            clan-lib-openapi
            module-docs
            ;
          inherit (inputs) nixpkgs;
        };
        deploy-docs = pkgs.callPackage ./deploy-docs.nix { inherit (config.packages) docs; };
      };
      checks.docs-integrity =
        pkgs.runCommand "docs-integrity"
          {
            nativeBuildInputs = [ pkgs.html-proofer ];
            LANG = "C.UTF-8";
          }
          ''
            # External links should be avoided in the docs, because they often break
            # and we cannot statically control them. Thus we disable checking them
            htmlproofer --disable-external ${self'.packages.docs}

            touch $out
          '';
    };
}
