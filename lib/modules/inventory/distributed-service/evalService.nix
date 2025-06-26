/*
  Example usage:

  ```nix
  evalService = import /this/file.nix { inherit lib clanLib; };
  result = evalService { modules = []; prefix = []; };

  => result.config
  => result.options
  ```
*/
{ lib, clanLib }:
# <lambda evalService>
{ modules, prefix }:
lib.evalModules {
  class = "clan.service";
  specialArgs._ctx = prefix;
  modules =
    [
      # Base module
      ./service-module.nix
      # Feature modules
      (lib.modules.importApply ./api-feature.nix {
        inherit clanLib prefix;
      })
    ]
    ++
    # Modules of caller
    modules;
}
