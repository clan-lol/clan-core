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
  clan.modules.certificates = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.certificates = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules.certificates = module;
      };
    };
}
