{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.p2p-ssh-iroh = module;
  perSystem =
    { ... }:
    {
      clan.nixosTests.p2p-ssh-iroh = {
        imports = [ ./tests/vm/default.nix ];
        clan.modules.p2p-ssh-iroh = module;
        clan.modules.sshd = ../sshd/default.nix;
      };
    };
}
