{
  module,
  ...
}:
{
  name = "hello-service";

  clan = {
    directory = ./.;
    inventory = {
      machines.peer1 = { };

      instances."test" = {
        module.name = "hello-service";
        module.input = "self";
        roles.peer.machines.peer1 = { };
      };
    };
  };

  testScript =
    { nodes, ... }:
    ''
      start_all()

      # peer1 should have the 'hello' file
      value = peer1.succeed("cat ${nodes.peer1.clan.core.vars.generators.hello.files.hello.path}")
      assert value.strip() == "Hello world from peer1", value
    '';
}
