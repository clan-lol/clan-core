{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.pki = module;

  perSystem =
    { ... }:
    {
      clan.nixosTests.pki = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules."@clan/pki" = module;
      };
    };
}
