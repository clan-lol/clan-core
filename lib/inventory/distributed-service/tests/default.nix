{
  lib,
  clanLib,
  ...
}:
let

  flakeInputsFixture = {
    upstream.clan.modules = {
      uzzi = {
        _class = "clan.service";
        manifest = {
          name = "uzzi-from-upstream";
        };
      };
    };
  };

  createTestClan =
    testClan:
    let
      res = clanLib.clan ({
        # Static / mocked
        specialArgs = {
          clan-core = {
            clan.modules = { };
          };
        };
        self.inputs = flakeInputsFixture // {
          self.clan = res.config;
        };
        directory = ./.;
        exportsModule = { };

        imports = [
          testClan
        ];
      });
    in
    res;

in
{
  extraModules = import ./extraModules.nix { inherit clanLib; };
  # exports = import ./exports.nix { inherit lib clanLib; };
  settings = import ./settings.nix { inherit lib createTestClan; };
  specialArgs = import ./specialArgs.nix { inherit lib createTestClan; };
  resolve_module_spec = import ./import_module_spec.nix {
    inherit lib createTestClan;
  };
  test_simple =
    let
      res = createTestClan {
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
        inventory.instances."instance_foo" = {
          module = {
            name = "simple-module";
          };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = res.config._services.mappedServices ? "<clan-core>-simple-module";
      expected = true;
      inherit res;
    };

  # A module can be imported multiple times
  # A module can also have multiple instances within the same module
  # This mean modules must be grouped together, imported once
  # All instances should be included within one evaluation to make all of them available
  test_module_grouping =
    let
      res = createTestClan {
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
        inventory.instances."instance_foo" = {
          module = {
            name = "A";
          };
        };
        inventory.instances."instance_bar" = {
          module = {
            name = "B";
          };
        };
        inventory.instances."instance_baz" = {
          module = {
            name = "A";
          };
        };
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.config._services.mappedServices;
      expected = [
        "<clan-core>-A"
        "<clan-core>-B"
      ];
    };

  test_creates_all_instances =
    let
      res = createTestClan {
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
        inventory = {
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
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.config._services.mappedServices.self-A.instances;
      expected = [
        "instance_bar"
        "instance_foo"
      ];
    };

  # Membership via roles
  test_add_machines_directly =
    let
      res = createTestClan {
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
        inventory = {
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
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.config._services.mappedServices.self-A.result.allMachines;
      expected = [
        "jon"
        "sara"
      ];
    };

  # Membership via tags
  test_add_machines_via_tags =
    let
      res = createTestClan {
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
        inventory = {
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
      };
    in
    {
      # Test that the module is mapped into the output
      # We might change the attribute name in the future
      expr = lib.attrNames res.config._services.mappedServices.self-A.result.allMachines;
      expected = [
        "jon"
        "sara"
      ];
    };

  machine_imports = import ./machine_imports.nix { inherit lib clanLib; };
  per_machine_args = import ./per_machine_args.nix { inherit lib createTestClan; };
  per_instance_args = import ./per_instance_args.nix {
    inherit lib;
    callInventoryAdapter = createTestClan;
  };
}
