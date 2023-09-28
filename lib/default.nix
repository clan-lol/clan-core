{ lib, self, nixpkgs, ... }:
{
  jsonschema = import ./jsonschema { inherit lib; };

  buildClan = import ./build-clan { inherit lib self nixpkgs; };
}
