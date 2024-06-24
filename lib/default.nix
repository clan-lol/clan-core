{
  lib,
  clan-core,
  nixpkgs,
  ...
}:
{
  evalClanModules = import ./eval-clan-modules { inherit clan-core nixpkgs lib; };
  jsonschema = import ./jsonschema { inherit lib; };
  modules = import ./description.nix { inherit clan-core lib; };
  buildClan = import ./build-clan { inherit clan-core lib nixpkgs; };
}
