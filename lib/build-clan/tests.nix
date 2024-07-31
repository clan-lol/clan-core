{
  lib,
  nixpkgs,
  clan-core,
  buildClan,
  ...
}:
let
  eval = import ./eval.nix { inherit lib nixpkgs clan-core; };

  self = ./.;
  evalClan = eval { inherit self; };

in
#######
{
  test_only_required =
    let
      config = evalClan { directory = ./.; };
    in
    {
      expr = config.pkgsForSystem null == null;
      expected = true;
    };

  test_all_simple =
    let
      config = evalClan {
        directory = ./.;
        machines = { };
        inventory = {
          meta.name = "test";
        };
        pkgsForSystem = _system: { };
      };
    in
    {
      expr = config ? inventory;
      expected = true;
    };

  test_outputs_clanInternals =
    let
      config = evalClan {
        imports = [
          # What the user needs to specif
          {
            directory = ./.;
            inventory.meta.name = "test";
          }

          # Build-clan implementation
          ./module.nix
          # Explicit output, usually defined by flake-parts
          { options.nixosConfigurations = lib.mkOption { type = lib.types.raw; }; }
        ];
      };
    in
    {
      expr = config.clanInternals.meta;
      expected = {
        description = null;
        icon = null;
        name = "test";
      };
    };

  test_fn_simple =
    let
      result = buildClan {
        directory = ./.;
        meta.name = "test";
      };
    in
    {
      expr = result.clanInternals.meta;
      expected = {
        description = null;
        icon = null;
        name = "test";
      };
    };

  test_fn_extensiv_meta =
    let
      result = buildClan {
        directory = ./.;
        meta.name = "test";
        meta.description = "test";
        meta.icon = "test";
        inventory.meta.name = "superclan";
        inventory.meta.description = "description";
        inventory.meta.icon = "icon";
      };
    in
    {
      expr = result.clanInternals.meta;
      expected = {
        description = "description";
        icon = "icon";
        name = "superclan";
      };
    };

  test_fn_clan_core =
    let
      result = buildClan {
        directory = ../../.;
        meta.name = "test-clan-core";
      };
    in
    {
      expr = builtins.attrNames result.nixosConfigurations;
      expected = [ "test-inventory-machine" ];
    };

  test_buildClan_all_machines =
    let
      result = buildClan {
        directory = ./.;
        meta.name = "test";
        inventory.machines.machine1.meta.name = "machine1";

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
}
