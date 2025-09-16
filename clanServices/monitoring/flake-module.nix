{
  ...
}:
let
  module = ./default.nix;
in
{
  clan.modules.monitoring = module;

  perSystem =
    { ... }:
    {
      clan.nixosTests.monitoring = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules.monitoring = module;
      };
    };
}
