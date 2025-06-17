{
  module,
  pkgs,
  ...
}:
{
  name = "ergochat";

  clan = {
    directory = ./.;
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
