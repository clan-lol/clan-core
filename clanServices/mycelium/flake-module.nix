{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    mycelium = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.mycelium = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/mycelium" = module;
      };
    };
}
