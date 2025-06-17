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
  clan.modules.wifi = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.wifi = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/wifi" = module;
      };
    };
}
