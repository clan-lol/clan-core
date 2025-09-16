{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.localbackup = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.localbackup = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/localbackup" = module;
      };
    };
}
