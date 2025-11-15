{
  self,
  lib,
  ...
}:
let
  module = ./default.nix;
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
