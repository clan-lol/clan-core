{ lib
, self
, ...
}: {
  flake.nixosModules = lib.mapAttrs (_: nix: { imports = [ nix ]; }) (self.lib.findNixFiles ../nixosModules);
}
