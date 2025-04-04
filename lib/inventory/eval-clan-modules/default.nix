{
  lib,
  clanLib,
}:
let
  baseModule =
    { pkgs }:
    # Module
    { config, ... }:
    {
      imports = (import (pkgs.path + "/nixos/modules/module-list.nix"));
      nixpkgs.pkgs = pkgs;
      clan.core.name = "dummy";
      system.stateVersion = config.system.nixos.release;
      # Set this to work around a bug where `clan.core.settings.machine.name`
      # is forced due to `networking.interfaces` being forced
      # somewhere in the nixpkgs options
      facter.detected.dhcp.enable = lib.mkForce false;
    };

  # This function takes a list of module names and evaluates them
  # [ module ] -> { config, options, ... }
  evalClanModulesLegacy =
    {
      modules,
      pkgs,
      clan-core,
    }:
    let
      evaled = lib.evalModules {
        modules = [
          (baseModule { inherit pkgs; })
          {
            clan.core.settings.directory = clan-core;
          }
          clan-core.nixosModules.clanCore
        ] ++ modules;
      };
    in
    # lib.warn ''
    #   doesn't respect role specific interfaces.

    #   The following {module}/default.nix file trying to be imported.

    #   Modules: ${builtins.toJSON modulenames}

    #   This might result in incomplete or incorrect interfaces.

    #   FIX: Use evalClanModuleWithRole instead.
    # ''
    evaled;

  /*
    This function takes a list of module names and evaluates them
    Returns a set of interfaces as described below:

    Fn :: { ${moduleName} = Module; } -> {
      ${moduleName} :: {
        ${roleName}: JSONSchema
      }
    }
  */
  evalClanModulesWithRoles =
    {
      allModules,
      clan-core,
      pkgs,
    }:
    let
      res = builtins.mapAttrs (
        moduleName: module:
        let
          frontmatter = clanLib.modules.getFrontmatter allModules.${moduleName} moduleName;
          roles =
            if builtins.elem "inventory" frontmatter.features or [ ] then
              assert lib.isPath module;
              clanLib.modules.getRoles allModules moduleName
            else
              [ ];
        in
        lib.listToAttrs (
          lib.map (role: {
            name = role;
            value =
              (lib.evalModules {
                modules = [
                  (baseModule { inherit pkgs; })
                  clan-core.nixosModules.clanCore
                  {
                    clan.core.settings.directory = clan-core;
                  }
                  # Role interface
                  (module + "/roles/${role}.nix")
                ];
              }).options.clan.${moduleName} or { };
          }) roles
        )
      ) allModules;
    in
    res;
in
{
  evalClanModules = evalClanModulesLegacy;
  inherit evalClanModulesWithRoles;
}
