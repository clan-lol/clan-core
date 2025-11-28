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
  autoloading = import ./dir_test.nix { inherit lib; };
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
        domain = "clan";
        tld = null;
      };
    };

  # Regression test: single letter TLD should be allowed
  test_single_letter_domain =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";
        meta.domain = "x";
      };
    in
    {
      expr = eval.config.clanInternals.inventoryClass.inventory.meta.domain;
      expected = "x";
    };

  # Regression test: domain with underscore should be allowed
  test_domain_with_underscore =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";
        meta.domain = "my_clan.x";
      };
    in
    {
      expr = eval.config.clanInternals.inventoryClass.inventory.meta.domain;
      expected = "my_clan.x";
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
        directory = ../.;
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
        directory = ../.;
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

  test_clan_check_simple_fail =
    let
      eval = clan {
        checks.constFail = {
          assertion = false;
          message = "This is a constant failure";
        };
      };
    in
    {
      result = eval;
      expr = eval.config;
      expectedError.type = "ThrownError";
      expectedError.msg = "This is a constant failure";
    };
  test_clan_check_simple_pass =
    let
      eval = clan {
        checks.constFail = {
          assertion = true;
          message = "This is a constant success";
        };
      };
    in
    {
      result = eval;
      expr = lib.seq eval.config 42;
      expected = 42;
    };

  test_get_var_machine =
    let
      varsLib = import ./vars.nix { inherit lib; };
    in
    {
      expr = varsLib.getPublicValue {
        backend = "in_repo";
        default = "test";
        generator = "test-generator";
        machine = "test-machine";
        file = "test-file";
        flake = ./vars-test-flake;
      };
      expected = "foo-machine";
    };

  test_get_var_shared =
    let
      varsLib = import ./vars.nix { inherit lib; };
    in
    {
      expr = varsLib.getPublicValue {
        backend = "in_repo";
        default = "test";
        generator = "test-generator";
        file = "test-file";
        flake = ./vars-test-flake;
      };
      expected = "foo-shared";
    };

  test_get_var_default =
    let
      varsLib = import ./vars.nix { inherit lib; };
    in
    {
      expr = varsLib.getPublicValue {
        backend = "in_repo";
        default = "test-default";
        generator = "test-generator-wrong";
        file = "test-file";
        flake = ./vars-test-flake;
      };
      expected = "test-default";
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

  test_clan_darwin_wireguard_service =
    let
      eval = clan {
        self = {
          inputs = { };
        };
        directory = ./.;
        meta.name = "test";
        # Set nixpkgs.hostPlatform for each machine to allow deep evaluation
        machines.nixos-peer.nixpkgs.hostPlatform = "x86_64-linux";
        machines.darwin-peer.nixpkgs.hostPlatform = "aarch64-darwin";
        machines.controller.nixpkgs.hostPlatform = "x86_64-linux";
        inventory = {
          machines.nixos-peer = { };
          machines.darwin-peer = {
            machineClass = "darwin";
          };
          machines.controller = { };
          instances.wg-test = {
            module.name = "wireguard";
            roles.controller.machines.controller.settings.endpoint = "192.168.1.1";
            roles.peer.machines.nixos-peer.settings.controller = "controller";
            roles.peer.machines.darwin-peer.settings.controller = "controller";
          };
        };
      };
      darwinConfig = eval.config.darwinConfigurations.darwin-peer.config;
      nixosConfig = eval.config.nixosConfigurations.nixos-peer.config;
    in
    {
      expr = {
        # Check machine configurations exist
        nixos = builtins.attrNames eval.config.nixosConfigurations;
        darwin = builtins.attrNames eval.config.darwinConfigurations;

        # Check darwin wg-quick interface is configured (option exists)
        darwinWgInterface = darwinConfig.networking.wg-quick.interfaces ? wg-test;

        # Check darwin has extraHosts option defined
        # We only check existence since evaluating the value requires vars to be generated
        darwinHasExtraHostsOption = darwinConfig.clan.core.networking ? extraHosts;

        # Check nixos wireguard interface is configured (option exists)
        nixosWgInterface = nixosConfig.networking.wireguard.interfaces ? wg-test;
      };
      expected = {
        nixos = [
          "controller"
          "nixos-peer"
        ];
        darwin = [ "darwin-peer" ];

        darwinWgInterface = true;
        darwinHasExtraHostsOption = true;
        nixosWgInterface = true;
      };
    };
}
