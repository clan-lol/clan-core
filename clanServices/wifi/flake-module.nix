{
  ...
}:
let
  module = ./default.nix;
in
{
  clan.modules.wifi = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.wifi = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/wifi" = module;
      };
    };
}
