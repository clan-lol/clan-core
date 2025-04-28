{ self, inputs, ... }:
{
  perSystem =
    {
      lib,
      pkgs,
      ...
    }:
    let
      # A flake lock for offline use.
      # All flake inputs are locked to an existing store path
      clanCoreLockFile =
        clanCore:
        let
          flakeLock = lib.importJSON (clanCore + "/flake.lock");
          flakeInputs = builtins.removeAttrs inputs [ "self" ];
          flakeLockVendoredDeps =
            flakeLock:
            flakeLock
            // {
              nodes =
                flakeLock.nodes
                // (lib.flip lib.mapAttrs flakeInputs (
                  name: _:
                  # remove follows and let 'nix flake lock' re-compute it later
                  # (lib.removeAttrs flakeLock.nodes.${name} ["inputs"])
                  flakeLock.nodes.${name}
                  // {
                    locked = {
                      inherit (flakeLock.nodes.${name}.locked) narHash;
                      lastModified =
                        # lol, nixpkgs has a different timestamp on the fs???
                        if name == "nixpkgs" then 0 else 1;
                      path = "${inputs.${name}}";
                      type = "path";
                    };
                  }
                ));
            };
          clanCoreLock = flakeLockVendoredDeps flakeLock;
          clanCoreLockFile = builtins.toFile "clan-core-flake.lock" (builtins.toJSON clanCoreLock);
        in
        clanCoreLockFile;
    in
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
                cp ${clanCoreLockFile clanCore} $out/flake.lock
                nix flake lock $out --extra-experimental-features 'nix-command flakes'
                clanCoreHash=$(nix hash path ${clanCore} --extra-experimental-features 'nix-command')
              '';
        in
        pkgs.callPackage package { clanCore = self; };
    };
}
