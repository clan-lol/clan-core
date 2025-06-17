{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules = {
    heisenbridge = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.heisenbridge = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/heisenbridge" = module;
      };
    };
}
