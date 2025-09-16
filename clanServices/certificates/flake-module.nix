{
  ...
}:
let
  module = ./default.nix;
in
{
  clan.modules.certificates = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.certificates = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules.certificates = module;
      };
    };
}
