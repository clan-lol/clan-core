# export some of our flake moduels for re-use in other projects
{ lib
, self
, ...
}: {
  flake.modules.flake-parts = {
    writers = ./writers;
  };
  flake.nixosModules = lib.mapAttrs (_: nix: { imports = [ nix ]; }) (self.lib.findNixFiles ../nixosModules);
  flake.clanModules = lib.mapAttrs (_: nix: { imports = [ nix ]; }) (self.lib.findNixFiles ../clanModules);
}
