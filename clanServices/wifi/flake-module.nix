{
  self,
  inputs,
  lib,
  ...
}:
let
  module = lib.modules.importApply ./default.nix {
    inherit (self) packages;
  };
in
{
  clan.inventory.modules = {
    wifi = module;
  };
  clan.modules = {
    wifi = module;
  };
  perSystem =
    { pkgs, ... }:
    {
      /**
        1. Prepare the test vars
        nix run .#generate-test-vars -- clanServices/hello-world/tests/vm hello-service

        2. To run the test
        nix build .#checks.x86_64-linux.hello-service
      */
      checks =
        # Currently we don't support nixos-integration tests on darwin
        lib.optionalAttrs (pkgs.stdenv.isLinux) {
          wifi-service = import ./tests/vm/default.nix {
            inherit module;
            inherit self inputs pkgs;
            clanLib = self.clanLib;
          };
        };
    };
}
