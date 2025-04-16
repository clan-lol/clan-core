{
  module,
  clanLib,
  ...
}:
let
  testFlake = clanLib.buildClan {
    # Point to the folder of the module
    # TODO: make this optional in buildClan
    directory = ./..;

    # Create some test machines
    machines.jon = {
      nixpkgs.hostPlatform = "x86_64-linux";
    };
    machines.sara = {
      nixpkgs.hostPlatform = "x86_64-linux";
    };

    # Register the module for the test
    inventory.modules.zerotier-redux = module;

    # Use the module in the test
    inventory.instances = {
      "zero" = {
        module.name = "zerotier-redux";

        roles.peer.machines.jon = { };
      };
    };
  };
  # NOTE:
  # If you wonder why 'self-zerotier-redux':
  # A local module has prefix 'self', otherwise it is the name of the 'input'
  # The rest is the name of the service as in the instance 'module.name';
  #
  # -> ${module.input}-${module.name}
  # In this case it is 'self-zerotier-redux'
  # This is usually only used internally, but we can use it to test the evaluation of service module in isolation
  # evaluatedService =
  #   testFlake.clanInternals.inventoryClass.distributedServices.importedModulesEvaluated.self-zerotier-redux.config;
in
{
  test_simple = {
    inherit testFlake;

    expr = {
    };
    expected = {

    };
  };
}
