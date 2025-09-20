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
    yggdrasil = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.yggdrasil = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.yggdrasil = module;
      };
    };
}
