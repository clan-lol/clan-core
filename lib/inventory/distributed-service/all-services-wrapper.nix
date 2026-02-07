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
    # exportsModule = mkOption {
    #   type = types.deferredModule;
    #   readOnly = true;
    # };
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
              availableTraits = ''
                Available traits

                ${lib.join "\n" (lib.attrNames exportInterfaces)}
              '';
              manifest = manifestByName.${name};
              enabledInterfaceModules = map (
                t:
                exportInterfaces.${t} or (throw ''
                  Export interface: '${t}' doesn't exist
                  Service: '${manifest.name}'

                  - Remove it from 'manifest.traits'
                  - Add it to 'clan.exportInterfaces.${t}'

                  ${availableTraits}
                '')
              ) manifest.traits;

              throwEnableTraits = lib.throwIf (lib.length manifest.traits == 0) ''
                Service: '${manifest.name}' doesn't allow exports

                - Add 'manifest.traits = [ ]' to the service

                ${availableTraits}
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

      # collect exports from all services
      # default =
      #   lib.zipAttrsWith
      #     (_name: imds: {
      #       imports =
      #         /**
      #           Enable 'trait' interfaces
      #         */
      #         map (t: exportInterfaces.${t} or (throw ''
      #           Service Trait: ${t} doesn't exist
      #           Service: '${(lib.head imds).service.manifest.name}'

      #           To define it set 'clan.exportInterfaces.${t}'
      #         '')) (lib.head imds).service.manifest.traits

      #         # Map the exports into them
      #         ++ (map (s: builtins.addErrorContext "" s.exports) imds);
      #     })
      #     (
      #       lib.mapAttrsToList (
      #         _service_id: service:
      #         lib.mapAttrs (
      #           exportName: exports:
      #           lib.seq
      #             (specialArgs.clanLib.checkScope {
      #               serviceName = service.manifest.name;
      #               errorDetails = ''
      #                 Export validation failed in service '${service.manifest.name}'

      #                 Context:
      #                   - Service: ${service.manifest.name}
      #                   - Source: exports

      #                 Problem: Services can only export to their own scope (here: "${service.manifest.name}:::")

      #                 Refer to https://docs.clan.lol for more information on exports.
      #               '';
      #             } exportName)

      #             # intermediate
      #             {
      #               inherit exports;
      #               inherit service;
      #             }
      #         ) service.exports
      #       ) config.mappedServices
      # );
    };
  };
}
