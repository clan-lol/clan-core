{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules = {
    garage = module;
  };

  perSystem =
    { ... }:
    {
      clan.nixosTests.garage = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/garage" = module;
      };
    };
}
