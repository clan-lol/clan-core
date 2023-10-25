{ lib, clan-core, nixpkgs, ... }:
{
  jsonschema = import ./jsonschema { inherit lib; };

  buildClan = import ./build-clan { inherit clan-core lib nixpkgs; };
}
