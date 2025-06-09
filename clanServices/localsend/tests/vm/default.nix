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

    name = "localsend";

    clan = {
      directory = ./.;
      modules."@clan/localsend" = ../../default.nix;
      inventory = {
        machines.server = { };

        instances = {
          localsend-test = {
            module.name = "@clan/localsend";
            roles.default.machines."server".settings = {
              displayName = "Test Instance";
              ipv4Addr = "192.168.56.2/24";
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

      # Check that the localsend wrapper script is available
      server.succeed("command -v localsend")

      # Verify the 09-zerotier network is configured with the specified IP address
      server.succeed("grep -q 'Address=192.168.56.2/24' /etc/systemd/network/09-zerotier.network")
    '';
  }
)
