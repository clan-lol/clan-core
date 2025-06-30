{
  name = "zerotier";

  clan = {
    directory = ./.;
    inventory = {

      machines.jon = { };
      machines.sara = { };
      machines.bam = { };

      instances = {
        "zerotier" = {
          module.name = "zerotier";
          module.input = "self";

          roles.peer.tags.all = { };
          roles.controller.machines.bam = { };
          roles.moon.machines = { };
        };
      };
    };
  };

  # This is not an actual vm test, this is a workaround to
  # generate the needed vars for the eval test.
  testScript = "";
}
