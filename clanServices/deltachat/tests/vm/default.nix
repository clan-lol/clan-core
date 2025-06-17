{
  module,
  pkgs,
  ...
}:
{
  name = "deltachat";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };

      instances = {
        deltachat-test = {
          module.name = "@clan/deltachat";
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

    server.wait_for_unit("maddy")

    # imap
    server.succeed("${pkgs.netcat}/bin/nc -z -v ::1 143")
    # smtp submission
    server.succeed("${pkgs.netcat}/bin/nc -z -v ::1 587")
    # smtp
    server.succeed("${pkgs.netcat}/bin/nc -z -v ::1 25")
  '';
}
