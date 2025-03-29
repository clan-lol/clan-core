{
  lib,
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
        ../../inventory/build-inventory/interface.nix
        {
          modules.test = { };
        }
        m
      ];
    }).config;

  flakeFixture = {
    inputs = { };
  };

  callInventoryAdapter =
    inventoryModule:
    import ../inventory-adapter.nix {
      inherit lib;
      flake = flakeFixture;
      inventory = evalInventory inventoryModule;
    };
in
{
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
      expr = res.evals ? "self-simple-module";
      expected = true;
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
        self-A = 2;
        self-B = 1;
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
          };
        };
        instances."instance_bar" = {
          module = {
            name = "A";
          };
        };
        instances."instance_zaza" = {
          module = {
            name = "B";
          };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.evals.self-A.config.instances;
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
          };
          roles.peer.machines.jon = { };
        };
        instances."instance_bar" = {
          module = {
            name = "A";
          };
          roles.peer.machines.sara = { };
        };
        instances."instance_zaza" = {
          module = {
            name = "B";
          };
          roles.peer.tags.all = { };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.evals.self-A.config.result.allMachines;
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
          };
          roles.peer.tags.foo = { };
        };
        instances."instance_zaza" = {
          module = {
            name = "B";
          };
          roles.peer.tags.all = { };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.evals.self-A.config.result.allMachines;
      expected = [
        "jon"
        "sara"
      ];
    };

  per_machine_args = import ./per_machine_args.nix { inherit lib callInventoryAdapter; };
  # test_per_machine_receives_instances =
  #   let
  #     res = callInventoryAdapter {
  #       # Authored module
  #       # A minimal module looks like this
  #       # It isn't exactly doing anything but it's a valid module that produces an output
  #       modules."A" = {
  #         _class = "clan.service";
  #         manifest = {
  #           name = "network";
  #         };
  #         # Define a role without special behavior
  #         roles.peer = { };

  #         perMachine =
  #           { instances, ... }:
  #           {
  #             nixosModule = instances;
  #           };
  #       };
  #       machines = {
  #         jon = { };
  #         sara = { };
  #       };
  #       instances."instance_foo" = {
  #         module = {
  #           name = "A";
  #         };
  #         roles.peer.machines.jon = { };
  #       };
  #       instances."instance_bar" = {
  #         module = {
  #           name = "A";
  #         };
  #         roles.peer.machines.sara = { };
  #       };
  #       instances."instance_zaza" = {
  #         module = {
  #           name = "B";
  #         };
  #         roles.peer.tags.all = { };
  #       };
  #     };
  #   in
  #   {
  #     expr = {
  #       hasMachineSettings =
  #         res.evals.self-A.config.result.allMachines.jon.nixosModule. # { {instanceName} :: { roles :: { {roleName} :: { machines :: { {machineName} :: { settings :: {} } } } } } }
  #         instance_foo.roles.peer.machines.jon ? settings;
  #       machineSettingsEmpty =
  #         lib.filterAttrs (n: _v: n != "__functor" ) res.evals.self-A.config.result.allMachines.jon.nixosModule. # { {instanceName} :: { roles :: { {roleName} :: { machines :: { {machineName} :: { settings :: {} } } } } } }
  #         instance_foo.roles.peer.machines.jon.settings;
  #       hasRoleSettings =
  #         res.evals.self-A.config.result.allMachines.jon.nixosModule. # { {instanceName} :: { roles :: { {roleName} :: { machines :: { {machineName} :: { settings :: {} } } } } } }
  #         instance_foo.roles.peer ? settings;
  #       roleSettingsEmpty =
  #         lib.filterAttrs (n: _v: n != "__functor" ) res.evals.self-A.config.result.allMachines.jon.nixosModule. # { {instanceName} :: { roles :: { {roleName} :: { machines :: { {machineName} :: { settings :: {} } } } } } }
  #         instance_foo.roles.peer.settings;
  #     };
  #     expected = {
  #       hasMachineSettings = true;
  #       machineSettingsEmpty = {};
  #       hasRoleSettings = true;
  #       roleSettingsEmpty = {};
  #     };
  #   };
}
