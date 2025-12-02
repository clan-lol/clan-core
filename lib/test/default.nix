{
  clanLib,
  lib,
}:
{
  containerTest = import ./container-test.nix;
  baseTest = import ./test-base.nix;

  flakeModules = import ./flakeModules.nix { inherit clanLib lib; };

  minifyModule = ./minify.nix;
  sopsModule = ./sops.nix;
}
