{
  clan-core,
  lib,
}:
lib.foldl' (acc: file: acc // (import file { inherit clan-core lib; })) { } [
  ./test_buildScopeKey.nix
  ./test_checkScope.nix
  ./test_parseScope.nix
  ./test_checkExports.nix
  ./test_selectExports.nix
  ./test_getExport.nix
  ./test_simple.nix
]
