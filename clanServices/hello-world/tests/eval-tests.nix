{
  module,
  clanLib,
  ...
}:
let
  testClan = clanLib.clan {
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
  /**
    We highly advocate the usage of:
    https://github.com/nix-community/nix-unit

    If you use flake-parts you can use the native integration: https://flake.parts/options/nix-unit.html
  */
  test_simple = {
    # Allows inspection via the nix-repl
    # Ignored by nix-unit; it only looks at 'expr' and 'expected'
    inherit testClan;

    # Assert that jon has the
    # configured greeting in 'environment.etc.hello.text'
    expr = testClan.config.nixosConfigurations.jon.config.environment.etc."hello".text;
    expected = "Good evening World!";
  };
}
