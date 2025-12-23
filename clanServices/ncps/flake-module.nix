{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    ncps = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.ncps = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/ncps" = module;
      };
    };
}
