{ lib, ... }:
{
  name = "service-state-version";

  clan = {
    directory = ./.;
    inventory = {
      machines.server = { };
      instances.default = {
        module.name = "@clan/state-version";
        module.input = "self";
        roles.default.machines."server" = { };
      };
    };
  };

  nodes.server = { };

  testScript = lib.mkDefault ''
    start_all()
  '';
}
