{
  clan-core,
  lib,
}:
let
  inherit (clan-core) clanLib;
in
{
  buildScopeKey = import ./test_buildScopeKey.nix { inherit clanLib lib; };
  checkScope = import ./test_checkScope.nix { inherit clanLib lib; };
  parseScope = import ./test_parseScope.nix { inherit clanLib lib; };
  checkExports = import ./test_checkExports.nix { inherit clanLib lib; };
  selectExports = import ./test_selectExports.nix { inherit clanLib lib; };
  getExport = import ./test_getExport.nix { inherit clanLib lib; };
  integration = import ./test_integration.nix { inherit clanLib lib; };
}
