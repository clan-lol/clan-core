{
  lib,
  clan-core,
}:
let
  # Shallowly force all attribute values to be evaluated.
  shallowForceAllAttributes = lib.foldlAttrs (
    _acc: _name: value:
    lib.seq value true
  ) true;
  inherit (clan-core.clanLib) clan;
in
#######
{
  test_missing_self =
    let
      eval = clan {
        meta.name = "test";
        directory = ./.;
      };
    in
    {
      expr = shallowForceAllAttributes eval.config;
      expected = true;
    };

  test_only_required =
    let
      eval = clan {
        self = {
          inputs = { };
          outPath = ./.;
        };
        meta.name = "test";
      };
    in
    {
      expr = shallowForceAllAttributes eval.config;
      expected = true;
    };

  test_all_simple =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        machines = { };
        inventory = {
          meta.name = "test";
        };
      };
    in
    {
      expr = eval.config ? inventory;
      expected = true;
    };

  test_outputs_clanInternals =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        imports = [
          # What the user needs to specify
          {
            directory = ./.;
            inventory.meta.name = "test";
          }
        ];
      };
    in
    {
      inherit eval;
      expr = eval.config.clanInternals.inventoryClass.inventory.meta;
      expected = {
        description = null;
        icon = null;
        name = "test";
      };
    };

  test_fn_simple =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";
      };
    in
    {
      expr = lib.isAttrs eval.config.clanInternals;
      expected = true;
    };

  test_fn_clan_core =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ../../.;
        meta.name = "test-clan-core";
      };
    in
    {
      expr = builtins.attrNames eval.config.nixosConfigurations;
      expected = [
        "test-backup"
        "test-inventory-machine"
      ];
    };

  test_machines_are_modules =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ../../.;
        meta.name = "test-clan-core";
      };
    in
    {
      expr = builtins.attrNames eval.config.nixosModules;
      expected = [
        "clan-machine-test-backup"
        "clan-machine-test-inventory-machine"
      ];
    };

  test_clan_all_machines =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";

        inventory.machines.machine1 = { };
        machines.machine2 = { };
      };
    in
    {
      expr = builtins.attrNames eval.config.nixosConfigurations;
      expected = [
        "machine1"
        "machine2"
      ];
    };

  test_clan_specialArgs =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";
        specialArgs.foo = "dream2nix";
        machines.machine2 =
          { foo, ... }:
          {
            networking.hostName = foo;
            nixpkgs.hostPlatform = "x86_64-linux";
          };
      };
    in
    {
      expr = eval.config.nixosConfigurations.machine2.config.networking.hostName;
      expected = "dream2nix";
    };

  test_clan_darwin_machines =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";

        machines.machine1 = { };
        inventory.machines.machine2 = {
          machineClass = "darwin";
        };
        inventory.machines.machine3 = {
          machineClass = "nixos";
        };
      };
    in
    {
      result = eval;
      expr = {
        nixos = builtins.attrNames eval.config.nixosConfigurations;
        darwin = builtins.attrNames eval.config.darwinConfigurations;
      };
      expected = {
        nixos = [
          "machine1"
          "machine3"
        ];
        darwin = [ "machine2" ];
      };
    };

  test_clan_all_machines_laziness =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";

        machines.machine1.non_existent_option = throw "eval error";
      };
    in
    {
      expr = builtins.attrNames eval.config.nixosConfigurations;
      expected = [
        "machine1"
      ];
    };
}
