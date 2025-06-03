{
  clanLib,
  ...
}:
{
  containerTest = import ./container-test.nix;
  baseTest = import ./test-base.nix;

  flakeModules = clanLib.callLib ./flakeModules.nix { };

  minifyModule = ./minify.nix;
  sopsModule = ./sops.nix;
}
