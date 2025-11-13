{ lib, clanLib, ... }:
{
  uniqueDeferredSerializableModule = import ./unique.nix { inherit lib clanLib; };
}
