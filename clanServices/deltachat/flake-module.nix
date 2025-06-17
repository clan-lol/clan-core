{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules = {
    deltachat = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.deltachat = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/deltachat" = module;
      };
    };
}
