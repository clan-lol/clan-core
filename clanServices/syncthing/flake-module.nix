{
  self,
  lib,
  ...
}:
let
  module = lib.modules.importApply ./default.nix {
    inherit (self) packages;
  };
in
{
  clan.modules = {
    syncthing = module;
  };
  perSystem =
    { ... }:
    {
      /**
        1. Prepare the test vars
        nix run .#generate-test-vars -- clanServices/syncthing/tests/vm syncthing-service

        2. To run the test
        nix build .#checks.x86_64-linux.syncthing-service
      */
      clan.nixosTests.syncthing-service = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.syncthing-service = module;
      };
    };
}
