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
    name = "ergochat";

    clan = {
      directory = ./.;
      modules."@clan/ergochat" = ../../default.nix;
      inventory = {
        machines.server = { };

        instances = {
          ergochat-test = {
            module.name = "@clan/ergochat";
            roles.default.machines."server".settings = { };
          };
        };
      };
    };

    nodes = {
      server = { };
    };

    testScript = ''
      start_all()

      server.wait_for_unit("ergochat")

      # Check that ergochat is running
      server.succeed("systemctl status ergochat")

      # Check that the data directory exists
      server.succeed("test -d /var/lib/ergo")

      # Check that the server is listening on the correct ports
      server.succeed("${pkgs.netcat}/bin/nc -z -v ::1 6667")
    '';
  }
)
