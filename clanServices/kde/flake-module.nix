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
  clan.modules = {
    kde = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.kde = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.kde = module;
      };
    };
}
