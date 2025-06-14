{ clanLib, lib, ... }:
{
  test_simple = import ./simple.nix { inherit clanLib lib; };
}
