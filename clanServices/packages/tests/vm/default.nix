{
  module,
  ...
}:
{
  name = "packages";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };

      instances.default = {
        module.name = "@clan/packages";
        roles.default.machines."server".settings = {
          packages = [ "cbonsai" ];
        };
      };
    };
  };

  nodes.server = { };

  testScript = ''
    start_all()
    server.succeed("cbonsai")
  '';
}
