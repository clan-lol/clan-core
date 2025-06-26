/*
  service-B :: Service
    exports a nixosModule which set "address" and "hostname"
    Note: How we use null together with mkIf to create optional values.
    This is a method, to create mergable modules

  service-A :: Service

  service-A.roles.server.perInstance.services."B"
    imports service-B
    configures a client with hostname = "johnny"

  service-A.perMachine.services."B"
    imports service-B
    configures a client with address = "root"
*/
{ clanLib, lib, ... }:
let
  service-B = (
    { lib, ... }:
    {
      manifest.name = "service-B";

      roles.client.interface = {
        options.hostname = lib.mkOption { default = null; };
        options.address = lib.mkOption { default = null; };
      };
      roles.client.perInstance =
        { settings, ... }:
        {
          nixosModule = {
            imports = [
              # Only export the value that is actually set.
              (lib.mkIf (settings.hostname != null) {
                hostname = settings.hostname;
              })
              (lib.mkIf (settings.address != null) {
                address = settings.address;
              })
            ];
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
      };
      instances.bar = {
        roles.server.machines."jon" = { };
      };

      roles.server = {
        perInstance =
          { machine, instanceName, ... }:
          {
            services."B" = {
              imports = [
                service-B
              ];
              instances."B-for-A" = {
                roles.client.machines.${machine.name} = {
                  settings.hostname = instanceName + "+johnny";
                };
              };
            };
          };
      };
      perMachine =
        { machine, ... }:
        {
          services."B" = {
            imports = [
              service-B
            ];
            instances."B-for-A" = {
              roles.client.machines.${machine.name} = {
                settings.address = "root";
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

  evalNixos = lib.evalModules {
    modules = [
      {
        options.assertions = lib.mkOption { };
        options.hostname = lib.mkOption { type = lib.types.separatedString " "; };
        options.address = lib.mkOption { type = lib.types.str; };
      }
      eval.config.result.final."jon".nixosModule
    ];
  };
in
{
  # Check that the nixos system has the settings from the nested module, as well as those from the "perMachine" and "perInstance"
  inherit eval;
  expr = evalNixos.config;
  expected = {
    address = "root";
    assertions = [ ];
    # Concatenates hostnames from both instances
    hostname = "bar+johnny foo+johnny";
  };
}
