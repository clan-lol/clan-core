{ clanLib, lib, ... }:
{
  test_simple = import ./simple.nix { inherit clanLib lib; };

  test_multi_machine = import ./multi_machine.nix { inherit clanLib lib; };

  test_multi_import_duplication = import ./multi_import_duplication.nix { inherit clanLib lib; };
}
