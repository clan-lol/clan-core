{ lib, ... }:
let
  inherit (lib) mkOption;
  inherit (lib.types)
    str
    listOf
    ;
in
{
  options = {
    hosts = mkOption {
      type = listOf str;
      default = [ ];
    };
  };
}
