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
  test_inventory_role_resolve =
    let
      eval = clan {
        directory = ./.;
        inventory = {
          services = {
            borgbackup.instance_1 = {
              roles.server.machines = [ "backup_server" ];
              roles.client.machines = [
                "client_1_machine"
                "client_2_machine"
              ];
            };
          };
          machines = {
            "backup_server" = { };
            "client_1_machine" = { };
            "client_2_machine" = { };
          };
        };
      };
    in
    {
      expr = {
        m1 =
          (eval.config.clanInternals.inventoryClass.machines."backup_server")
          .compiledServices.borgbackup.matchedRoles;
        m2 =
          (eval.config.clanInternals.inventoryClass.machines."client_1_machine")
          .compiledServices.borgbackup.matchedRoles;
        m3 =
          (eval.config.clanInternals.inventoryClass.machines."client_2_machine")
          .compiledServices.borgbackup.matchedRoles;
        inherit
          ((eval.config.clanInternals.inventoryClass.machines."client_2_machine").compiledServices.borgbackup)
          resolvedRolesPerInstance
          ;
      };

      expected = {
        m1 = [
          "server"
        ];
        m2 = [
          "client"
        ];
        m3 = [
          "client"
        ];
        resolvedRolesPerInstance = {
          instance_1 = {
            client = {
              machines = [
                "client_1_machine"
                "client_2_machine"
              ];
            };
            server = {
              machines = [ "backup_server" ];
            };
          };
        };
      };
    };
  test_inventory_tag_resolve =
    let
      eval = clan {
        directory = ./.;
        inventory = {
          services = {
            borgbackup.instance_1 = {
              roles.client.tags = [ "backup" ];
            };
          };
          machines = {
            "not_used_machine" = { };
            "client_1_machine" = {
              tags = [ "backup" ];
            };
            "client_2_machine" = {
              tags = [ "backup" ];
            };
          };
        };
      };
    in
    {
      expr =
        eval.config.clanInternals.inventoryClass.machines.client_1_machine.compiledServices.borgbackup.resolvedRolesPerInstance;
      expected = {
        instance_1 = {
          client = {
            machines = [
              "client_1_machine"
              "client_2_machine"
            ];
          };
          server = {
            machines = [ ];
          };
        };
      };
    };

  test_inventory_multiple_roles =
    let
      eval = clan {
        directory = ./.;
        inventory = {
          services = {
            borgbackup.instance_1 = {
              roles.client.machines = [ "machine_1" ];
              roles.server.machines = [ "machine_1" ];
            };
          };
          machines = {
            "machine_1" = { };
          };
        };
      };
    in
    {
      expr =
        eval.config.clanInternals.inventoryClass.machines.machine_1.compiledServices.borgbackup.matchedRoles;
      expected = [
        "client"
        "server"
      ];
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

  test_inventory_role_doesnt_exist =
    let
      eval = clan {
        directory = ./.;
        inventory = {
          services = {
            borgbackup.instance_1 = {
              roles.roleXYZ.machines = [ "machine_1" ];
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
        msg = ''Roles \["roleXYZ"\] are not defined in the service borgbackup'';
      };
    };
  # Needs NIX_ABORT_ON_WARN=1
  # So the lib.warn is turned into abort
  test_inventory_tag_doesnt_exist =
    let
      eval = clan {
        directory = ./.;
        inventory = {
          services = {
            borgbackup.instance_1 = {
              roles.client.machines = [ "machine_1" ];
              roles.client.tags = [ "tagXYZ" ];
            };
          };
          machines = {
            "machine_1" = {
              tags = [ "tagABC" ];
            };
          };
        };
      };
    in
    {
      expr = eval.config.clanInternals.inventoryClass.machines.machine_1.machineImports;
      expectedError = {
        type = "Error";
        # TODO: Add warning matching in nix-unit
        msg = ".*";
      };
    };
  test_inventory_disabled_service =
    let
      eval = clan {
        directory = ./.;
        inventory = {
          services = {
            borgbackup.instance_1 = {
              enabled = false;
              roles.client.machines = [ "machine_1" ];
            };
          };
          machines = {
            "machine_1" = {

            };
          };
        };
      };
    in
    {
      inherit eval;
      expr = builtins.filter (
        v: v != { } && !v.clan.inventory.assertions ? "alive.assertion.inventory"
      ) eval.config.clanInternals.inventoryClass.machines.machine_1.machineImports;
      expected = [ ];
    };
}
