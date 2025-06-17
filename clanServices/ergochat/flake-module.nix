{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules = {
    ergochat = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.ergochat = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/ergochat" = module;
      };
    };
}
