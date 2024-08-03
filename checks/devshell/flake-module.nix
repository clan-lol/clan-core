{ ... }:
{
  perSystem =
    { self', pkgs, ... }:
    {
      checks.devshell =
        pkgs.runCommand "check-devshell-not-depends-on-clan-cli"
          {
            exportReferencesGraph = [
              "graph"
              self'.devShells.default
            ];
          }
          ''
            if grep -q "${self'.packages.clan-cli}" ./graph; then
              echo "devshell depends on clan-cli, which is not allowed";
              exit 1;
            fi
            mkdir $out
          '';
    };
}
