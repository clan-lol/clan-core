## WARNING: Do not add core logic here.
## This is only a wrapper such that 'clan' can be called as a function.
{
  lib,
  clan-core,
  ...
}:
rec {
  buildClan =
    # TODO: Once all templates and docs are migrated add: lib.warn "'buildClan' is deprecated. Use 'clan-core.lib.clan' instead"
    module: (clan module).config;

  clan =
    {
      self ? lib.warn "Argument: 'self' must be set" null, # Reference to the current flake
      ...
    }@m:
    let
      nixpkgs = self.inputs.nixpkgs or clan-core.inputs.nixpkgs;
      nix-darwin = self.inputs.nix-darwin or clan-core.inputs.nix-darwin;
    in
    lib.evalModules {
      class = "clan";
      specialArgs = {
        inherit
          self
          ;
        inherit
          nixpkgs
          nix-darwin
          ;
      };
      modules = [
        m
        clan-core.modules.clan.default
      ];
    };
}
