{
  lib,
  self,
  ...
}:
let
  module = ./default.nix;
in
{
  clan.modules.monitoring = module;

  perSystem =
    { pkgs, ... }:
    {
      clan.nixosTests.monitoring = {
        imports = [
          (lib.modules.importApply ./tests/vm/default.nix {
            inherit (self) packages;
            inherit pkgs;
          })
        ];
        clan.modules.monitoring = module;
      };
    };
}
