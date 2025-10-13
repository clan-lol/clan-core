{
  lib ? import <nixpkgs/lib>,
}:
let
  clanLibOrig = (import ./.. { inherit lib; }).__unfix__;
  clanLibWithFs =
    { virtual_fs }:
    lib.fix (
      lib.extends (
        final: _:
        let
          clan-core = {
            clanLib = final;
            modules.clan.default = lib.modules.importApply ./clan { inherit clan-core; };

            # Note: Can add other things to "clan-core"
            # ... Not needed for this test
          };
        in
        {
          clan = import ../clan {
            inherit lib clan-core;
          };

          # Override clanLib.fs for unit-testing against a virtual filesystem
          fs = import ../clanTest/virtual-fs.nix { inherit lib; } {
            inherit rootPath virtual_fs;
            # Example of a passthru
            # passthru = [
            #   ".*inventory\.json$"
            # ];
          };
        }
      ) clanLibOrig
    );

  rootPath = ./.;
in
{
  test_autoload_directories =
    let
      vclan =
        (clanLibWithFs {
          virtual_fs = {
            "machines" = {
              type = "directory";
            };
            "machines/foo-machine" = {
              type = "directory";
            };
            "machines/bar-machine" = {
              type = "directory";
            };
          };
        }).clan
          { config.directory = rootPath; };
    in
    {
      inherit vclan;
      expr = {
        machines = lib.attrNames vclan.config.inventory.machines;
        definedInMachinesDir = map (
          p: lib.hasInfix "/machines/" p
        ) vclan.options.inventory.valueMeta.configuration.options.machines.files;
      };
      expected = {
        machines = [
          "bar-machine"
          "foo-machine"
        ];
        definedInMachinesDir = [
          true # /machines/foo-machine
          true # /machines/bar-machine
          false # <clan-core>/module.nix defines "machines" without members
        ];
      };
    };

  # Could probably be unified with the previous test
  # This is here for the sake to show that 'virtual_fs' is a test parameter
  test_files_are_not_machines =
    let
      vclan =
        (clanLibWithFs {
          virtual_fs = {
            "machines" = {
              type = "directory";
            };
            "machines/foo.nix" = {
              type = "file";
            };
            "machines/bar.nix" = {
              type = "file";
            };
          };
        }).clan
          { config.directory = rootPath; };
    in
    {
      inherit vclan;
      expr = {
        machines = lib.attrNames vclan.config.inventory.machines;
      };
      expected = {
        machines = [ ];
      };
    };
}
