{
  modulesRolesOptions,
  nixosOptionsDoc,
  evalClanModules,
  lib,
  pkgs,
  clan-core,
  ...
}:
let
  inherit (clan-core.clanLib.docs) stripStorePathsFromDeclarations;
  transformOptions = stripStorePathsFromDeclarations;
in
{

  clanModulesViaRoles = lib.mapAttrs (
    _moduleName: rolesOptions:
    lib.mapAttrs (
      _roleName: options:
      (nixosOptionsDoc {
        inherit options;
        warningsAreErrors = true;
        inherit transformOptions;
      }).optionsJSON
    ) rolesOptions
  ) modulesRolesOptions;

  # Test with:
  # nix build .\#legacyPackages.x86_64-linux.clanModulesViaService
  clanModulesViaService = lib.mapAttrs (
    _moduleName: moduleValue:
    let
      evaluatedService = clan-core.clanLib.evalService {
        modules = [ moduleValue ];
        prefix = [ ];
      };
    in
    {
      roles = lib.mapAttrs (
        _roleName: role:

        (nixosOptionsDoc {
          transformOptions =
            opt:
            let
              # Apply store path stripping first
              transformed = transformOptions opt;
            in
            if lib.strings.hasPrefix "_" transformed.name then
              transformed // { visible = false; }
            else
              transformed;
          options = (lib.evalModules { modules = [ role.interface ]; }).options;
          warningsAreErrors = true;
        }).optionsJSON
      ) evaluatedService.config.roles;

      manifest = evaluatedService.config.manifest;

    }
  ) clan-core.clan.modules;

  clanCore =
    (nixosOptionsDoc {
      options =
        ((evalClanModules {
          modules = [ ];
          inherit pkgs clan-core;
        }).options
        ).clan.core or { };
      warningsAreErrors = true;
      inherit transformOptions;
    }).optionsJSON;
}
