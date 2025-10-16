{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.wireguard = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.service-wireguard = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules."@clan/wireguard" = module;
      };
    };
}
