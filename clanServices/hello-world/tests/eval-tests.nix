{
  module,
  clanLib,
  ...
}:
let
  testFlake = clanLib.clan {
    self = { };
    # Point to the folder of the module
    # TODO: make this optional
    directory = ./..;

    # Create some test machines
    machines.jon = {
      nixpkgs.hostPlatform = "x86_64-linux";
    };
    machines.sara = {
      nixpkgs.hostPlatform = "x86_64-linux";
    };

    # Register the module for the test
    modules.hello-world = module;

    # Use the module in the test
    inventory.instances = {
      "hello" = {
        module.name = "hello-world";
        module.input = "self";

        roles.evening.machines.jon = { };
      };
    };
  };
in
{
  test_simple = {
    config = testFlake.config;

    expr = { };
    expected = { };
  };
}
