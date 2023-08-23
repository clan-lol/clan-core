{
  perSystem =
    { pkgs
    , self'
    , ...
    }: {
      devShells.default = pkgs.mkShell {
        packages = [
          pkgs.tea
          self'.packages.tea-create-pr
          self'.packages.merge-after-ci
        ];
        shellHook = ''
          ln -sf ../../scripts/pre-commit "$(git rev-parse --show-toplevel)/.git/hooks/pre-commit"
        '';
      };
    };
}
