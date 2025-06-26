{ clanLib, lib, ... }:
let
  service-B = (
    { lib, ... }:
    {
      manifest.name = "service-B";

      roles.client.interface = {
        options.user = lib.mkOption { };
        options.host = lib.mkOption { };
      };
      roles.client.perInstance =
        { settings, instanceName, ... }:
        {
          nixosModule = {
            units.${instanceName} = {
              script = settings.user + "@" + settings.host;
            };
          };
        };
      perMachine =
        { ... }:
        {
          nixosModule = {
            ssh.enable = true;
          };
        };
    }
  );
  service-A =
    { ... }:
    {
      manifest.name = "service-A";

      instances.foo = {
        roles.server.machines."jon" = { };
        roles.server.machines."sara" = { };
      };

      roles.server = {
        perInstance =
          { machine, instanceName, ... }:
          {
            services."B" = {
              imports = [
                service-B
              ];
              instances."A-${instanceName}-B" = {
                roles.client.machines.${machine.name} = {
                  settings.user = "johnny";
                  settings.host = machine.name;
                };
              };
            };
          };
      };
    };

  eval = clanLib.evalService {
    modules = [
      (service-A)
    ];
    prefix = [ ];
  };

  evalNixos = lib.mapAttrs (
    _n: v:
    (lib.evalModules {
      modules = [
        {
          options.assertions = lib.mkOption { };
          options.units = lib.mkOption { };
          options.ssh = lib.mkOption { };
        }
        v.nixosModule
      ];
    }).config
  ) eval.config.result.final;
in
{
  # Check that the nixos system has the settings from the nested module, as well as those from the "perMachine" and "perInstance"
  inherit eval;
  expr = evalNixos;
  expected = {
    jon = {
      assertions = [ ];
      ssh = {
        enable = true;
      };
      units = {
        A-foo-B = {
          script = "johnny@jon";
        };
      };
    };
    sara = {
      assertions = [ ];
      ssh = {
        enable = true;
      };
      units = {
        A-foo-B = {
          script = "johnny@sara";
        };
      };
    };
  };
}
