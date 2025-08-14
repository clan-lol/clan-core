{
  self,
  lib,
  ...
}:
let
  module = lib.modules.importApply ./default.nix {
    inherit (self) packages;
  };
in
{
  clan.modules.monitoring = module;

  perSystem =
    { ... }:
    {
      clan.nixosTests.monitoring = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.monitoring = module;
      };
    };
}
