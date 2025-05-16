{
  modulesRolesOptions,
  nixosOptionsDoc,
  clanModules,
  evalClanModules,
  lib,
  pkgs,
  clan-core,
}:
{
  # clanModules docs
  clanModulesViaNix = lib.mapAttrs (
    name: module:
    if builtins.pathExists (module + "/default.nix") then
      (nixosOptionsDoc {
        options =
          ((evalClanModules {
            modules = [ module ];
            inherit pkgs clan-core;
          }).options
          ).clan.${name} or { };
        warningsAreErrors = true;
      }).optionsJSON
    else
      { }
  ) clanModules;

  clanModulesViaRoles = lib.mapAttrs (
    _moduleName: rolesOptions:
    lib.mapAttrs (
      _roleName: options:
      (nixosOptionsDoc {
        inherit options;
        warningsAreErrors = true;
      }).optionsJSON
    ) rolesOptions
  ) modulesRolesOptions;

  # Test with:
  # nix build .\#legacyPackages.x86_64-linux.clanModulesViaService
  clanModulesViaService = lib.mapAttrs (
    _moduleName: moduleValue:
    let
      evaluatedService = clan-core.clanLib.inventory.evalClanService {
        modules = [ moduleValue ];
        prefix = [ ];
      };
    in
    {
      roles = lib.mapAttrs (
        _roleName: role:

        (nixosOptionsDoc {
          transformOptions =
            opt: if lib.strings.hasPrefix "_" opt.name then opt // { visible = false; } else opt;
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
    }).optionsJSON;
}
