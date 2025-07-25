{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules = {
    admin = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.admin = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/admin" = module;
      };
    };
}
