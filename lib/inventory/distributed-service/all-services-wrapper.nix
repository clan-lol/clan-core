# Wraps all services in one fixed point module
{
  # TODO: consume directly from clan.config
  directory,
  exports,
}:
{
  lib,
  config,
  specialArgs,
  _ctx,
  ...
}:
let
  inherit (lib) mkOption types;
  inherit (types) attrsWith submoduleWith;
in
{
  # TODO: merge these options into clan options
  options = {
    # exportsModule = mkOption {
    #   type = types.deferredModule;
    #   readOnly = true;
    # };
    mappedServices = mkOption {
      visible = false;
      type = attrsWith {
        placeholder = "mappedServiceName";
        elemType = submoduleWith {
          class = "clan.service";
          specialArgs = {
            clanLib = specialArgs.clanLib;
            inherit
              exports
              directory
              ;
          };
          modules = [
            (
              { name, ... }:
              {
                _module.args._ctx = [ name ];
              }
            )
            ./service-module.nix
            #  feature modules
            (lib.modules.importApply ./api-feature.nix {
              inherit (specialArgs) clanLib;
              prefix = _ctx;
            })
          ];
        };
      };
      default = { };
    };
    exports = mkOption {
      type = types.lazyAttrsOf types.deferredModule;

      # collect exports from all services
      # zipAttrs is needed until we use the record type.
      default = lib.zipAttrsWith (_name: values: { imports = values; }) (
        lib.mapAttrsToList (
          _service_id: service:
          specialArgs.clanLib.checkExports {
            serviceName = service.manifest.name;
            errorDetails = ''
              Export validation failed in service '${service.manifest.name}'

              Context:
                - Service: ${service.manifest.name}
                - Source: exports

              Problem: Services can only export to their own scope (here: "${service.manifest.name}:::")

              Refer to https://docs.clan.lol for more information on exports.
            '';
          } service.exports
        ) config.mappedServices
      );
    };
  };
}
