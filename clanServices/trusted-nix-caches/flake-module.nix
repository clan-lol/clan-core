{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules.trusted-nix-caches = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.trusted-nix-caches = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/trusted-nix-caches" = module;
      };
    };
}
