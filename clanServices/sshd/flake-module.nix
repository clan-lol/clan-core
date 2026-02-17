{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    sshd = module;
  };

  perSystem =
    { ... }:
    {
      clan.nixosTests.sshd = {
        imports = [ ./tests/vm/default.nix ];

        clan.modules."@clan/sshd" = module;
      };
    };

}
