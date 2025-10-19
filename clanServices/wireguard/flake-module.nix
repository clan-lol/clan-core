{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.wireguard = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.wireguard = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules."@clan/wireguard" = module;
      };
    };
}
