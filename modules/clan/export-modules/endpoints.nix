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
    name = mkOption {
      type = listOf str;
      default = [ ];
    };
  };
}
