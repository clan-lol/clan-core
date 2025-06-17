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
    wifi = module;
  };
  perSystem =
    { ... }:
    {
      /**
        1. Prepare the test vars
        nix run .#generate-test-vars -- clanServices/hello-world/tests/vm hello-service

        2. To run the test
        nix build .#checks.x86_64-linux.hello-service
      */
      clan.nixosTests.wifi-service = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/wifi" = module;
      };
    };
}
