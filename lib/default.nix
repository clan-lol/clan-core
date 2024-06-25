{
  lib,
  clan-core,
  nixpkgs,
  ...
}:
{
  evalClanModules = import ./eval-clan-modules { inherit clan-core nixpkgs lib; };
  inventory = import ./inventory { inherit lib clan-core; };
  jsonschema = import ./jsonschema { inherit lib; };
  # TODO: migrate to also use toml frontmatter
  # modules = import ./description.nix { inherit clan-core lib; };
  buildClan = import ./build-clan { inherit clan-core lib nixpkgs; };
}
