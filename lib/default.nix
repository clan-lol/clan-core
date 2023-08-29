{ lib, clan, nixpkgs, ... }:
{
  findNixFiles = folder:
    lib.mapAttrs'
      (name: type:
        if
          type == "directory"
        then
          lib.nameValuePair name "${folder}/${name}"
        else
          lib.nameValuePair (lib.removeSuffix ".nix" name) "${folder}/${name}"
      )
      (builtins.readDir folder);

  jsonschema = import ./jsonschema { inherit lib; };

  buildClan = import ./build-clan { inherit lib clan nixpkgs; };
}
