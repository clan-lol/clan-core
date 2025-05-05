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
    inventory.modules.wifi = module;

    # Use the module in the test
    inventory.instances = {
      "default" = {
        module.name = "wifi";
        roles.default.tags.all = { };
        roles.default.settings.networks.one = { };
        roles.default.settings.networks.two = { };
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

    expr =
      testFlake.clanInternals.inventoryClass.distributedServices.importedModulesEvaluated.self-wifi.config;
    expected = 1;

    # expr = {
    # };
    # expected = {
    #
    # };
  };
}
