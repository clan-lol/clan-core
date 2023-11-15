{ inputs, self, lib, ... }:
{
  perSystem = { self', pkgs, system, ... }:
    let
      flakeLock = lib.importJSON (self + /flake.lock);
      flakeInputs = (builtins.removeAttrs inputs [ "self" ]);
      flakeLockVendoredDeps = flakeLock // {
        nodes = flakeLock.nodes // (
          lib.flip lib.mapAttrs flakeInputs (name: _: flakeLock.nodes.${name} // {
            locked = {
              inherit (flakeLock.nodes.${name}.locked) narHash;
              lastModified =
                # lol, nixpkgs has a different timestamp on the fs???
                if name == "nixpkgs"
                then 0
                else 1;
              path = "${inputs.${name}}";
              type = "path";
            };
          })
        );
      };
      flakeLockFile = builtins.toFile "clan-core-flake.lock"
        (builtins.toJSON flakeLockVendoredDeps);
      clanCoreWithVendoredDeps = lib.trace flakeLockFile pkgs.runCommand "clan-core-with-vendored-deps" { } ''
        cp -r ${self} $out
        chmod +w -R $out
        cp ${flakeLockFile} $out/flake.lock
      '';
    in
    {
      devShells.clan-cli = pkgs.callPackage ./shell.nix {
        inherit (self'.packages) clan-cli ui-assets nix-unit;
      };
      packages = {
        clan-cli = pkgs.python3.pkgs.callPackage ./default.nix {
          inherit (self'.packages) ui-assets;
          inherit (inputs) nixpkgs;
          inherit (inputs.nixpkgs-for-deal.legacyPackages.${system}.python3Packages) deal;
          clan-core-path = clanCoreWithVendoredDeps;
        };
        inherit (self'.packages.clan-cli) clan-openapi;
        default = self'.packages.clan-cli;
      };

      checks = self'.packages.clan-cli.tests;
    };

}
