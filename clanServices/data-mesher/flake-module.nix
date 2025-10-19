{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    data-mesher = module;
  };
  perSystem =
    { ... }:
    {
      clan.nixosTests.data-mesher = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules."@clan/data-mesher" = module;
      };
    };
}
