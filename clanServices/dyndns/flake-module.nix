{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    dyndns = module;
  };

  perSystem =
    { ... }:
    {
      clan.nixosTests.dyndns = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/dyndns" = module;
      };
    };
}
