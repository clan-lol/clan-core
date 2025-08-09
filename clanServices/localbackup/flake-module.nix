{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules.localbackup = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.localbackup = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/localbackup" = module;
      };
    };
}
