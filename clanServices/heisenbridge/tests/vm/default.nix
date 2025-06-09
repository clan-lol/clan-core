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

    name = "heisenbridge";

    clan = {
      directory = ./.;
      modules."@clan/heisenbridge" = ../../default.nix;
      inventory = {
        machines.server = { };

        instances = {
          heisenbridge-test = {
            module.name = "@clan/heisenbridge";
            roles.default.machines."server".settings = {
              homeserver = "http://127.0.0.1:8008";
            };
          };
        };
      };
    };

    nodes = {
      server = {
        # Setup a minimal matrix-synapse to test with
        services.matrix-synapse = {
          enable = true;
          settings.server_name = "example.com";
          settings.database = {
            name = "sqlite3";
          };
        };
      };
    };

    testScript = ''
      start_all()

      server.wait_for_unit("matrix-synapse")
      server.wait_for_unit("heisenbridge")

      # Check that heisenbridge is running
      server.succeed("systemctl status heisenbridge")

      # Wait for the bridge to initialize
      server.wait_until_succeeds("journalctl -u heisenbridge | grep -q 'bridge is now running'")

      # Check that heisenbridge is listening on the default port
      server.succeed("${pkgs.netcat}/bin/nc -z -v 127.0.0.1 9898")
    '';
  }
)
