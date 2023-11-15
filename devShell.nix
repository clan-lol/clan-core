{
  perSystem =
    { pkgs
    , self'
    , config
    , ...
    }: {
      devShells.default = pkgs.mkShell {
        packages = [
          pkgs.tea
          self'.packages.tea-create-pr
          self'.packages.merge-after-ci
          self'.packages.pending-reviews
          # treefmt with config defined in ./flake-parts/formatting.nix
          config.treefmt.build.wrapper
        ];
        shellHook = ''
          # no longer used
          rm -f "$(git rev-parse --show-toplevel)/.git/hooks/pre-commit"
        '';
      };
    };
}
