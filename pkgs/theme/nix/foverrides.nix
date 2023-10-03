{ lib, config, ... }:
let
  pjs = lib.importJSON ../package.json;
  ident = pjs.name;
  inherit (pjs) version;
in
{
  config.floco.packages.${ident}.${version} =
    {
      source = lib.libfloco.cleanLocalSource ../.;
    };
}
