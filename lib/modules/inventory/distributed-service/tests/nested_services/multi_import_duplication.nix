{ clanLib, lib, ... }:
let
  # Potentially imported many times
  # To add the ssh key
  example-admin = (
    { lib, ... }:
    {
      manifest.name = "example-admin";

      roles.client.interface = {
        options.keys = lib.mkOption { };
      };

      roles.client.perInstance =
        { settings, ... }:
        {
          nixosModule = {
            inherit (settings) keys;
          };
        };
    }
  );

  consumer-A =
    { ... }:
    {
      manifest.name = "consumer-A";

      instances.foo = {
        roles.server.machines."jon" = { };
      };
      instances.bar = {
        roles.server.machines."jon" = { };
      };

      roles.server = {
        perInstance =
          { machine, instanceName, ... }:
          {
            services."example-admin" = {
              imports = [
                example-admin
              ];
              instances."${instanceName}" = {
                roles.client.machines.${machine.name} = {
                  settings.keys = [ "pubkey-1" ];
                };
              };
            };
          };
      };
    };
  consumer-B =
    { ... }:
    {
      manifest.name = "consumer-A";

      instances.foo = {
        roles.server.machines."jon" = { };
      };
      instances.bar = {
        roles.server.machines."jon" = { };
      };

      roles.server = {
        perInstance =
          { machine, instanceName, ... }:
          {
            services."example-admin" = {
              imports = [
                example-admin
              ];
              instances."${instanceName}" = {
                roles.client.machines.${machine.name} = {
                  settings.keys = [
                    "pubkey-1"
                  ];
                };
              };
            };
          };
      };
    };

  eval = clanLib.inventory.evalClanService {
    modules = [
      (consumer-A)
    ];
    prefix = [ ];
  };
  eval2 = clanLib.inventory.evalClanService {
    modules = [
      (consumer-B)
    ];
    prefix = [ ];
  };

  evalNixos = lib.evalModules {
    modules = [
      {
        options.assertions = lib.mkOption { };
        # This is suboptimal
        options.keys = lib.mkOption { };
      }
      eval.config.result.final.jon.nixosModule
      eval2.config.result.final.jon.nixosModule
    ];
  };
in
{
  # Check that the nixos system has the settings from the nested module, as well as those from the "perMachine" and "perInstance"
  inherit eval;
  expr = evalNixos.config;
  expected = {
    assertions = [ ];
    # TODO: Some deduplication mechanism is nice
    # Could add types.set or do 'apply = unique', or something else ?
    keys = [
      "pubkey-1"
      "pubkey-1"
      "pubkey-1"
      "pubkey-1"
    ];
  };
}
