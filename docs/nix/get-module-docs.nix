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
