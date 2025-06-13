{
  pkgs,
  nixosLib,
  clan-core,
  module,
  ...
}:
nixosLib.runTest (
  { ... }:
  {
    imports = [
      clan-core.modules.nixosVmTest.clanTest
    ];

    hostPkgs = pkgs;

    name = "zerotier";

    clan = {
      directory = ./.;
      modules."zerotier" = module;
      inventory = {

        machines.jon = { };
        machines.sara = { };
        machines.bam = { };

        instances = {
          "zerotier" = {
            module.name = "zerotier";

            roles.peer.tags.all = { };
            roles.controller.machines.bam = { };
          };
        };
      };
    };

    # This is not an actual vm test, this is a workaround to
    # generate the needed vars for the eval test.
    testScript = '''';
  }
)
