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
  modules = [
    # Base module
    ./inventory/distributed-service/service-module.nix
    # Feature modules
    (lib.modules.importApply ./inventory/distributed-service/api-feature.nix {
      inherit clanLib prefix;
    })
  ]
  ++
    # Modules of caller
    modules;
}
