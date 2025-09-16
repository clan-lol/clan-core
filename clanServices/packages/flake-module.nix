{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    packages = module;
  };

  perSystem =
    { ... }:
    {
      clan.nixosTests.packages = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/packages" = module;
      };
    };

}
