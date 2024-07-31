{
  lib,
  clan-core,
  nixpkgs,
  ...
}:
{
  evalClanModules = import ./eval-clan-modules { inherit clan-core nixpkgs lib; };
  buildClan = import ./build-clan { inherit lib nixpkgs clan-core; };
  facts = import ./facts.nix { inherit lib; };
  inventory = import ./inventory { inherit lib clan-core; };
  jsonschema = import ./jsonschema { inherit lib; };
  modules = import ./description.nix { inherit clan-core lib; };
}
