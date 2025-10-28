## WARNING: Do not add core logic here.
## This is only a wrapper such that 'clan' can be called as a function.
{
  lib,
  clan-core,
}:
/**
  Function that takes clan options as function arguments.

  It behaves equivalent to:

  ```nix
  {
    imports = [
      clan-core.modules.clan.default
      args
    ];
  }
  ```

  Arguments:

  - self: Reference to the current flake. This is required be passed.
  - ...: All other arguments - Which are options as of the 'clan.*' module

  Returns:
  The clan configuration.
*/
{
  self ? lib.warn "Argument: 'self' must be set" null, # Reference to the current flake
  ...
}@m:
let
  nixpkgs = self.inputs.nixpkgs or clan-core.inputs.nixpkgs;
  nix-darwin = self.inputs.nix-darwin or clan-core.inputs.nix-darwin;
  configuration = (
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
        clan-core.modules.clan.default
        m
      ];
    }
  );
in
clan-core.clanLib.checkConfig configuration.config.checks configuration
