{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules.state-version = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.state-version = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/state-version" = module;
      };
    };
}
