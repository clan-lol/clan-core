{ self, ... }:
let
  inherit (self.clanLib.flakes)
    mkOfflineFlakeLock
    ;
in
{
  perSystem =
    {
      pkgs,
      ...
    }:
    {
      packages.clan-core-flake =
        let
          package =
            {
              clanCore,
            }:
            pkgs.runCommand "clan-core-flake"
              {
                buildInputs = [
                  pkgs.findutils
                  pkgs.git
                  pkgs.jq
                  pkgs.nix
                ];
              }
              ''
                set -e
                export HOME=$(realpath .)
                export NIX_STATE_DIR=$HOME
                export NIX_STORE_DIR=$HOME
                cp -r ${clanCore} $out
                chmod +w -R $out
                cp ${mkOfflineFlakeLock self} $out/flake.lock
                nix flake lock $out --extra-experimental-features 'nix-command flakes'
                clanCoreHash=$(nix hash path ${clanCore} --extra-experimental-features 'nix-command')
              '';
        in
        pkgs.callPackage package {
          clanCore = self.filter {
            name = "clan-core-source-without-tests";
            exclude = [
              (
                _root: path: _type:
                (builtins.match ".*/test_[^/]+\.py" path) != null # matches test_*.py
                || (builtins.match ".*/[^/]+_test\.py" path) != null # matches *_test.py
              )
              # exclude all pkgs/clan-cli/clan_cli/tests, except flake-module.nix
              (
                _root: path: _type:
                (builtins.match ".*/pkgs/clan-cli/clan_cli/tests/.*" path) != null
                && (builtins.match ".*/pkgs/clan-cli/clan_cli/tests/flake-module\.nix" path) == null
              )
            ];
          };
        };
    };
}
