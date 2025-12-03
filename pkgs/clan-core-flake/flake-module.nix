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

                # Marker file to disable private flake loading in tests
                touch $out/.skip-private-inputs
              '';
        in
        pkgs.callPackage package { clanCore = self; };
    };
}
