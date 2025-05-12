{ lib, clanLib }:
let
  # Trim the .nix extension from a filename
  trimExtension = name: builtins.substring 0 (builtins.stringLength name - 4) name;

  jsonWithoutHeader = clanLib.jsonschema {
    includeDefaults = true;
    header = { };
  };

  getModulesSchema =
    {
      modules,
      clan-core,
      pkgs,
    }:
    lib.mapAttrs
      (
        _moduleName: rolesOptions:
        lib.mapAttrs (_roleName: options: jsonWithoutHeader.parseOptions options { }) rolesOptions
      )
      (
        clanLib.evalClan.evalClanModulesWithRoles {
          allModules = modules;
          inherit pkgs clan-core;
        }
      );

  evalFrontmatter =
    {
      moduleName,
      instanceName,
      resolvedRoles,
      allModules,
    }:
    lib.evalModules {
      modules = [
        (getFrontmatter allModules.${moduleName} moduleName)
        ./interface.nix
        {
          constraints.imports = [
            (lib.modules.importApply ../constraints {
              inherit moduleName resolvedRoles instanceName;
              allRoles = getRoles "inventory.modules" allModules moduleName;
            })
          ];
        }
      ];
    };

  # For Documentation purposes only
  frontmatterOptions =
    (lib.evalModules {
      modules = [
        ./interface.nix
        {
          constraints.imports = [
            (lib.modules.importApply ../constraints {
              moduleName = "{moduleName}";
              allRoles = [ "{roleName}" ];
            })
          ];
        }
      ];
    }).options;

  # This is a legacy function
  # Old modules needed to define their roles by directory
  # This means if this function gets anything other than a string/path it will throw
  getRoles =
    scope: allModules: serviceName:
    let
      module =
        allModules.${serviceName}
          or (throw "(Legacy) ClanModule not found: '${serviceName}'. Make sure the module is added to ${scope}");
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

  checkConstraints = args: (evalFrontmatter args).config.constraints.assertions;

  getReadme =
    modulepath: modulename:
    let
      readme = modulepath + "/README.md";
      readmeContents =
        if (builtins.pathExists readme) then
          (builtins.readFile readme)
        else
          throw "No README.md found for module ${modulename} (expected at ${readme})";
    in
    readmeContents;

  getFrontmatter =
    modulepath: modulename:
    let
      content = getReadme modulepath modulename;
      parts = lib.splitString "---" content;
      # Partition the parts into the first part (the readme content) and the rest (the metadata)
      parsed = builtins.partition ({ index, ... }: if index >= 2 then false else true) (
        lib.filter ({ index, ... }: index != 0) (lib.imap0 (index: part: { inherit index part; }) parts)
      );
      meta = builtins.fromTOML (builtins.head parsed.right).part;
    in
    if (builtins.length parts >= 3) then
      meta
    else
      throw ''
        TOML Frontmatter not found in README.md for module ${modulename}

        Please add the following to the top of your README.md:

        ---
        description = "Your description here"
        categories = [ "Your categories here" ]
        features = [ "inventory" ]
        ---
        ...rest of your README.md...
      '';
in
{
  inherit
    frontmatterOptions
    getModulesSchema
    getFrontmatter

    checkConstraints
    getRoles
    ;
}
