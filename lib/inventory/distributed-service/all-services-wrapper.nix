# Wraps all services in one fixed point module
{
  directory,
  exports,
  exportInterfaces,
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
    allServices = mkOption {
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
      # Passthrough
      type = types.lazyAttrsOf types.raw;
      default =
        let
          # 1. collect all exports
          # 2. group exports by name
          # 3. merge exports with the enabled interfaces
          allExports = lib.mapAttrsToList (_id: service: service.exports) config.allServices;
          allManifests = lib.mapAttrsToList (
            _id: service: lib.mapAttrs (_n: _v: service.manifest) service.exports
          ) config.allServices;

          # Service exports cannot collide.
          # That means manifests for one export are always the same
          manifestByName = lib.zipAttrsWith (_key: ms: lib.head ms) allManifests;

          mergedByName = lib.zipAttrsWith (
            name: exports:
            let
              availableContract = ''
                Available export interfaces

                ${lib.join "\n" (lib.attrNames exportInterfaces)}
              '';
              manifest = manifestByName.${name};
              enabledInterfaceModules = map (
                t:
                exportInterfaces.${t} or (throw ''
                  Export interface: '${t}' doesn't exist
                  Service: '${manifest.name}'

                  - Remove it from 'manifest.exports.out'
                  - Add it to 'clan.exportInterfaces.${t}'

                  ${availableContract}
                '')
              ) manifest.exports.out;

              throwEnableTraits = lib.throwIf (lib.length manifest.exports.out == 0) ''
                Service: '${manifest.name}' doesn't allow exports

                - Add 'manifest.exports.out = [ ]' to the service

                ${availableContract}
              '';

              checked = (
                specialArgs.clanLib.checkScope {
                  serviceName = manifest.name;
                  errorDetails = ''
                    Export validation failed in service '${manifest.name}'

                    Context:
                      - Service: ${manifest.name}
                      - Source: exports

                    Problem: Services can only export to their own scope (here: "${manifest.name}:::")
                  '';
                } name
              );
            in
            lib.seq checked {
              imports = throwEnableTraits exports ++ enabledInterfaceModules;
            }
          ) allExports;
        in
        mergedByName;
    };
  };
}
