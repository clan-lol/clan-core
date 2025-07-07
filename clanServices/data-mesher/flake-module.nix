{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules = {
    data-mesher = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.service-data-mesher = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules."@clan/data-mesher" = module;
      };
    };
}
