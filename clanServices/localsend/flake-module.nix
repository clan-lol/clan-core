{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules = {
    localsend = module;
  };

  perSystem =
    { ... }:
    {
      clan.nixosTests.localsend = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/localsend" = module;
      };
    };
}
