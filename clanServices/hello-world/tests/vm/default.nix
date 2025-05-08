{
  pkgs,
  self,
  clanLib,
  module,
  ...
}:
clanLib.test.makeTestClan {
  inherit pkgs self;
  nixosTest = (
    { ... }:
    {
      name = "service-hello-test";

      clan = {
        directory = ./.;
        modules = {
          hello-service = module;
        };
        inventory = {
          machines.peer1 = { };

          instances."test" = {
            module.name = "hello-service";
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
  );
}
