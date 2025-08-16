{ lib, clanLib }:
let
  # Trim the .nix extension from a filename
  trimExtension = name: builtins.substring 0 (builtins.stringLength name - 4) name;

  # For Documentation purposes only
  frontmatterOptions =
    (lib.evalModules {
      modules = [
        ./interface.nix
        {
          constraints.imports = [
            (lib.modules.importApply ../constraints {
              resolvedRoles = { };
              moduleName = "{moduleName}";
              instanceName = "{instanceName}";
              allRoles = [ "{roleName}" ];
            })
          ];
        }
      ];
    }).options;

  migratedModules = [ ];

  makeModuleNotFoundError =
    serviceName:
    if builtins.elem serviceName migratedModules then
      ''
        (Legacy) ClanModule not found: '${serviceName}'.

        Please update your configuration to use this module via 'inventory.instances'
        See: https://docs.clan.lol/guides/clanServices/
      ''
    else
      ''
        (Legacy) ClanModule not found: '${serviceName}'.

        Make sure the module is added to inventory.modules.${serviceName}
      '';
  # This is a legacy function
  # Old modules needed to define their roles by directory
  # This means if this function gets anything other than a string/path it will throw
  getRoles =
    _scope: allModules: serviceName:
    let
      module = allModules.${serviceName} or (throw (makeModuleNotFoundError serviceName));
      moduleType = (lib.typeOf module);
      checked =
        if
          builtins.elem moduleType [
            "string"
            "path"
          ]
        then
          true
        else
          throw "(Legacy) ClanModule must be a 'path' or 'string' pointing to a directory: Got 'typeOf inventory.modules.${serviceName}' => ${moduleType} ";
      modulePath = lib.seq checked module + "/roles";
      checkedPath =
        if builtins.pathExists modulePath then
          modulePath
        else
          throw ''
            (Legacy) ClanModule must have a 'roles' directory'

            Fixes:
            - Provide a 'roles' subdirectory
            - Use the newer 'clan.service' modules. (Recommended)
          '';
    in
    lib.seq checkedPath lib.mapAttrsToList (name: _value: trimExtension name) (
      lib.filterAttrs (name: type: type == "regular" && lib.hasSuffix ".nix" name) (
        builtins.readDir (checkedPath)
      )
    );
  getFrontmatter = _modulepath: _modulename: "clanModules are removed!";
in
{
  inherit
    frontmatterOptions
    getFrontmatter
    getRoles
    ;
}
