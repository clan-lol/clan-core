{
  perSystem =
    { pkgs
    , self'
    , config
    , ...
    }: {
      devShells.default = pkgs.mkShell {
        inputsFrom = [
          config.pre-commit.devShell
          config.treefmt.build.devShell
        ];
        packages = [
          pkgs.tea
          self'.packages.tea-create-pr
          self'.packages.merge-after-ci
        ];
      };
    };
}
