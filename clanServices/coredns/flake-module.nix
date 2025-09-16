{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    coredns = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.coredns = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/coredns" = module;
      };
    };
}
