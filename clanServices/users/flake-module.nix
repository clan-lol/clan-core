{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.users = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.users = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/users" = module;
      };
    };
}
