{ lib, ... }:
let
  module = lib.modules.importApply ./default.nix { };
in
{
  clan.modules.matrix-synapse = module;

  perSystem =
    { ... }:
    {
      clan.nixosTests.matrix-synapse = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules."@clan/matrix-synapse" = module;
      };
    };
}
