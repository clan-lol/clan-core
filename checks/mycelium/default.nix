{
  pkgs,
  nixosLib,
  clan-core,
  ...
}:
nixosLib.runTest (
  { ... }:
  {
    imports = [
      clan-core.modules.nixosVmTest.clanTest
    ];

    hostPkgs = pkgs;

    name = "mycelium";

    clan = {

      test.useContainers = false;
      directory = ./.;
      modules."@clan/mycelium" = ../../clanServices/mycelium/default.nix;
      inventory = {
        machines.server = { };

        instances = {
          mycelium-test = {
            module.name = "@clan/mycelium";
            roles.peer.machines."server".settings = {
              openFirewall = true;
              addHostedPublicNodes = true;
            };
          };
        };
      };
    };

    nodes = {
      server = { };
    };

    testScript = ''
      start_all()

      # Check that mycelium service is running
      server.wait_for_unit("mycelium")
      server.succeed("systemctl status mycelium")

      # Check that mycelium is listening on its default port
      server.wait_until_succeeds("${pkgs.iproute2}/bin/ss -tulpn | grep -q 'mycelium'", 10)
    '';
  }
)
