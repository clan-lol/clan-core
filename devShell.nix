{
  perSystem =
    { pkgs
    , self'
    , config
    , ...
    }: {
      devShells.default = pkgs.mkShell {
        inputsFrom = [
          config.treefmt.build.devShell
        ];
        packages = [
          pkgs.tea
          self'.packages.tea-create-pr
          self'.packages.merge-after-ci
        ];
        shellHook = ''
          ln -sf ../../scripts/pre-commit .git/hooks/pre-commit
        '';
      };
    };
}
