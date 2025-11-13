{ lib, clanLib, ... }:
{
  uniqueDeferredSerializableModule = import ./unique.nix { inherit lib clanLib; };
  exclusiveDeferredModule = import ./exclusive.nix { inherit lib clanLib; };
}
