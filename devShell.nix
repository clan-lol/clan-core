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
          # treefmt with config defined in ./flake-parts/formatting.nix
          config.treefmt.build.wrapper
        ];
        shellHook = ''
          ln -sf ../../scripts/pre-commit "$(git rev-parse --show-toplevel)/.git/hooks/pre-commit"
        '';
      };
    };
}
