{
  lib,
  nixpkgs,
  clan-core,
  buildClan,
  ...
}:
let
  evalClan = import ./function-adapter.nix {
    inherit lib nixpkgs clan-core;
    self = ./.;
  };

  # Shallowly force all attribute values to be evaluated.
  shallowForceAllAttributes = lib.foldlAttrs (
    _acc: _name: value:
    lib.seq value true
  ) true;
in
#######
{
  test_missing_self =
    let
      config = buildClan {
        meta.name = "test";
        imports = [ ./module.nix ];
      };
    in
    {
      expr = shallowForceAllAttributes config;
      expectedError = {
        type = "ThrownError";
        msg = "A definition for option `directory' is not of type `absolute path*";
      };
    };

  test_only_required =
    let
      config = evalClan {
        self = {
          inputs = { };
          outPath = ./.;
        };
        meta.name = "test";
        imports = [ ./module.nix ];
      };
    in
    {
      expr = shallowForceAllAttributes config;
      expected = true;
    };

  test_all_simple =
    let
      config = evalClan {
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
      expr = config ? inventory;
      expected = true;
    };

  test_outputs_clanInternals =
    let
      config = evalClan {
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

          ./module.nix
          # Explicit output, usually defined by flake-parts
          { options.nixosConfigurations = lib.mkOption { type = lib.types.raw; }; }
        ];
      };
    in
    {
      expr = config.clanInternals.inventory.meta;
      expected = {
        description = null;
        icon = null;
        name = "test";
      };
    };

  test_fn_simple =
    let
      result = buildClan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";
      };
    in
    {
      expr = lib.isAttrs result.clanInternals;
      expected = true;
    };

  test_fn_clan_core =
    let
      result = buildClan {
        self = {
          inputs = { };
        };
        directory = ../../.;
        meta.name = "test-clan-core";
      };
    in
    {
      expr = builtins.attrNames result.nixosConfigurations;
      expected = [
        "test-backup"
        "test-inventory-machine"
      ];
    };

  test_machines_are_modules =
    let
      result = buildClan {
        self = {
          inputs = { };
        };
        directory = ../../.;
        meta.name = "test-clan-core";
      };
    in
    {
      expr = builtins.attrNames result.nixosModules;
      expected = [
        "clan-machine-test-backup"
        "clan-machine-test-inventory-machine"
      ];
    };

  test_buildClan_all_machines =
    let
      result = buildClan {
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
      expr = builtins.attrNames result.nixosConfigurations;
      expected = [
        "machine1"
        "machine2"
      ];
    };

  test_buildClan_specialArgs =
    let
      result = buildClan {
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
      expr = result.nixosConfigurations.machine2.config.networking.hostName;
      expected = "dream2nix";
    };

  test_buildClan_darwin_machines =
    let
      result = buildClan {
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
      inherit result;
      expr = {
        nixos = builtins.attrNames result.nixosConfigurations;
        darwin = builtins.attrNames result.darwinConfigurations;
      };
      expected = {
        nixos = [
          "machine1"
          "machine3"
        ];
        darwin = [ "machine2" ];
      };
    };

  test_buildClan_all_machines_laziness =
    let
      result = buildClan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";

        machines.machine1.non_existent_option = throw "eval error";
      };
    in
    {
      expr = builtins.attrNames result.nixosConfigurations;
      expected = [
        "machine1"
      ];
    };
}
