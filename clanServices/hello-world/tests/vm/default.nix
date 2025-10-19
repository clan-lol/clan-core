{
  name = "hello-service";

  clan = {
    directory = ./.;
    inventory = {
      machines.peer1 = { };
      machines.peer2 = { };

      instances."test" = {
        module.name = "hello-service";
        module.input = "self";

        # Assign the roles to the two machines
        roles.morning.machines.peer1 = { };

        roles.evening.machines.peer2 = {
          # Set roles settings for the peers, where we want to differ from
          # the role defaults
          settings = {
            greeting = "Good night";
          };
        };
      };
    };
  };

  testScript =
    { ... }:
    ''
      start_all()

      value = peer1.succeed("greet-world")
      assert value.strip() == "Good morning World! I'm peer1", value

      value = peer2.succeed("greet-world")
      assert value.strip() == "Good night World! I'm peer2", value
    '';
}
