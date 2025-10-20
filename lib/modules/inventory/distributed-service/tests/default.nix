{
  lib,
  clanLib,
  ...
}:
let
  inherit (lib)
    evalModules
    ;

  evalInventory =
    m:
    (evalModules {
      # Static modules
      modules = [
        clanLib.inventory.inventoryModule
        {
          _file = "test file";
          tags.all = [ ];
          tags.nixos = [ ];
          tags.darwin = [ ];
        }
        {
          modules.test = { };
        }
        m
      ];
    }).config;

  callInventoryAdapter =
    inventoryModule:
    let
      inventory = evalInventory inventoryModule;
      flakeInputsFixture = {
        self.clan.modules = inventoryModule.modules or { };
        # Example upstream module
        upstream.clan.modules = {
          uzzi = {
            _class = "clan.service";
            manifest = {
              name = "uzzi-from-upstream";
            };
          };
        };
      };
    in
    clanLib.inventory.mapInstances {
      directory = ./.;
      clanCoreModules = { };
      flakeInputs = flakeInputsFixture;
      inherit inventory;
      exportsModule = { };
    };
in
{
  extraModules = import ./extraModules.nix { inherit clanLib; };
  exports = import ./exports.nix { inherit lib clanLib; };
  settings = import ./settings.nix { inherit lib callInventoryAdapter; };
  resolve_module_spec = import ./import_module_spec.nix { inherit lib callInventoryAdapter; };
  test_simple =
    let
      res = callInventoryAdapter {
        # Authored module
        # A minimal module looks like this
        # It isn't exactly doing anything but it's a valid module that produces an output
        modules."simple-module" = {
          _class = "clan.service";
          manifest = {
            name = "netwitness";
          };
        };
        # User config
        instances."instance_foo" = {
          module = {
            name = "simple-module";
          };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = res.importedModulesEvaluated ? "<clan-core>-simple-module";
      expected = true;
      inherit res;
    };

  # A module can be imported multiple times
  # A module can also have multiple instances within the same module
  # This mean modules must be grouped together, imported once
  # All instances should be included within one evaluation to make all of them available
  test_module_grouping =
    let
      res = callInventoryAdapter {
        # Authored module
        # A minimal module looks like this
        # It isn't exactly doing anything but it's a valid module that produces an output
        modules."A" = {
          _class = "clan.service";
          manifest = {
            name = "A-name";
          };

          perMachine = { }: { };
        };
        modules."B" = {
          _class = "clan.service";
          manifest = {
            name = "B-name";
          };

          perMachine = { }: { };
        };
        # User config
        instances."instance_foo" = {
          module = {
            name = "A";
          };
        };
        instances."instance_bar" = {
          module = {
            name = "B";
          };
        };
        instances."instance_baz" = {
          module = {
            name = "A";
          };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.mapAttrs (_n: v: builtins.length v) res.grouped;
      expected = {
        "<clan-core>-A" = 2;
        "<clan-core>-B" = 1;
      };
    };

  test_creates_all_instances =
    let
      res = callInventoryAdapter {
        # Authored module
        # A minimal module looks like this
        # It isn't exactly doing anything but it's a valid module that produces an output
        modules."A" = {
          _class = "clan.service";
          manifest = {
            name = "network";
          };

          perMachine = { }: { };
        };
        instances."instance_foo" = {
          module = {
            name = "A";
            input = "self";
          };
        };
        instances."instance_bar" = {
          module = {
            name = "A";
            input = "self";
          };
        };
        instances."instance_zaza" = {
          module = {
            name = "B";
            input = null;
          };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.importedModulesEvaluated.self-A.instances;
      expected = [
        "instance_bar"
        "instance_foo"
      ];
    };

  # Membership via roles
  test_add_machines_directly =
    let
      res = callInventoryAdapter {
        # Authored module
        # A minimal module looks like this
        # It isn't exactly doing anything but it's a valid module that produces an output
        modules."A" = {
          _class = "clan.service";
          manifest = {
            name = "network";
            input = null;
          };
          # Define a role without special behavior
          roles.peer = { };

          # perMachine = {}: {};
        };
        machines = {
          jon = { };
          sara = { };
          hxi = { };
        };
        instances."instance_foo" = {
          module = {
            name = "A";
            input = "self";
          };
          roles.peer.machines.jon = { };
        };
        instances."instance_bar" = {
          module = {
            name = "A";
            input = "self";
          };
          roles.peer.machines.sara = { };
        };
        instances."instance_zaza" = {
          module = {
            name = "B";
            input = null;
          };
          roles.peer.tags.all = { };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.importedModulesEvaluated.self-A.result.allMachines;
      expected = [
        "jon"
        "sara"
      ];
    };

  # Membership via tags
  test_add_machines_via_tags =
    let
      res = callInventoryAdapter {
        # Authored module
        # A minimal module looks like this
        # It isn't exactly doing anything but it's a valid module that produces an output
        modules."A" = {
          _class = "clan.service";
          manifest = {
            name = "network";
          };
          # Define a role without special behavior
          roles.peer = { };

          # perMachine = {}: {};
        };
        machines = {
          jon = {
            tags = [ "foo" ];
          };
          sara = {
            tags = [ "foo" ];
          };
          hxi = { };
        };
        instances."instance_foo" = {
          module = {
            name = "A";
            input = "self";
          };
          roles.peer.tags.foo = { };
        };
        instances."instance_zaza" = {
          module = {
            name = "B";
            input = null;
          };
          roles.peer.tags.all = { };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.importedModulesEvaluated.self-A.result.allMachines;
      expected = [
        "jon"
        "sara"
      ];
    };

  machine_imports = import ./machine_imports.nix { inherit lib clanLib; };
  per_machine_args = import ./per_machine_args.nix { inherit lib callInventoryAdapter; };
  per_instance_args = import ./per_instance_args.nix { inherit lib callInventoryAdapter; };
}
