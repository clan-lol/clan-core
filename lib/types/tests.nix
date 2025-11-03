{ lib, clanLib, ... }:
let
  evalSettingsModule =
    m:
    lib.evalModules {
      modules = [
        {
          options.foo = lib.mkOption {
            type = clanLib.types.uniqueDeferredSerializableModule;
          };
        }
        m
      ];
    };
in
{
  uniqueDeferredSerializableModule = import ./unique.nix { inherit lib clanLib; };
  exclusiveDeferredModule = import ./exclusive.nix { inherit lib clanLib; };
}
