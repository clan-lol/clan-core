{
  clan-core,
  nix-darwin,
  lib,
  clanLib,
}:
let
  # TODO: Unify these tests with clan tests
  clan =
    m:
    lib.evalModules {
      specialArgs = { inherit clan-core nix-darwin clanLib; };
      modules = [
        clan-core.modules.clan.default
        {
          self = { };
        }
        m
      ];
    };
in
{
  test_inventory_a =
    let
      eval = clan {
        inventory = {
          machines = {
            A = { };
          };
          services = {
            legacyModule = { };
          };
          modules = {
            legacyModule = ./legacyModule;
          };
        };
        directory = ./.;
      };
    in
    {
      inherit eval;
      expr = {
        legacyModule = lib.filterAttrs (
          name: _: name == "isClanModule"
        ) eval.config.clanInternals.inventoryClass.machines.A.compiledServices.legacyModule;
      };
      expected = {
        legacyModule = {
        };
      };
    };

  test_inventory_empty =
    let
      eval = clan {
        inventory = { };
        directory = ./.;
      };
    in
    {
      # Empty inventory should return an empty module
      expr = eval.config.clanInternals.inventoryClass.machines;
      expected = { };
    };

  test_inventory_module_doesnt_exist =
    let
      eval = clan {
        directory = ./.;
        inventory = {
          services = {
            fanatasy.instance_1 = {
              roles.default.machines = [ "machine_1" ];
            };
          };
          machines = {
            "machine_1" = { };
          };
        };
      };
    in
    {
      inherit eval;
      expr = eval.config.clanInternals.inventoryClass.machines.machine_1.machineImports;
      expectedError = {
        type = "ThrownError";
        msg = "ClanModule not found*";
      };
    };
}
