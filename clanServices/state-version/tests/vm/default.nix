{
  name = "state-version";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };
      instances.default = {
        module.name = "@clan/state-version";
        roles.default.machines."server" = { };
      };
    };
  };

  nodes.server = { };

  testScript = ''
    start_all()
  '';
}
