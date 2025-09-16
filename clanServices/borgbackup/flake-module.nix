{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    borgbackup = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.borgbackup = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/borgbackup" = module;
      };
    };
}
