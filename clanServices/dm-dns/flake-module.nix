{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.dm-dns = module;

  perSystem =
    { ... }:
    {
      clan.nixosTests.dm-dns = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules."@clan/dm-dns" = module;
      };
    };
}
