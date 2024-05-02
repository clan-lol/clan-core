{ self, ... }:
{
  perSystem =
    { pkgs, lib, ... }:
    let
      clanModules = self.clanModules;

      # Uncomment if you only want one module to be available
      # clanModules = {
      #   syncthing = self.clanModules.syncthing;
      # };

      baseModule = {
        imports = (import (pkgs.path + "/nixos/modules/module-list.nix")) ++ [
          {
            nixpkgs.hostPlatform = "x86_64-linux";
            clanCore.clanName = "dummy";
          }
        ];
      };

      optionsFromModule =
        modulename: module:
        let
          evaled = lib.evalModules {
            modules = [
              module
              baseModule
              self.nixosModules.clanCore
            ];
          };
        in
        if (evaled.options.clan ? "${modulename}") then evaled.options.clan.${modulename} else { };

      clanModuleSchemas = lib.mapAttrs (
        modulename: module: self.lib.jsonschema.parseOptions (optionsFromModule modulename module)
      ) clanModules;

      clanModuleFunctionSchemas = lib.mapAttrsFlatten (modulename: module: {
        name = modulename;
        description = self.lib.modules.getShortDescription modulename;
        parameters = self.lib.jsonschema.parseOptions (optionsFromModule modulename module);
      }) clanModules;
    in
    rec {
      checks = {
        module-schema = pkgs.runCommand "schema-checks" { } ''
          ${pkgs.check-jsonschema}/bin/check-jsonschema \
            --check-metaschema --fill-defaults ${packages.module-schema}
          touch $out
        '';
      };

      packages = {
        module-schema = pkgs.runCommand "jsonschema" { } ''
          MSCHEMA=${builtins.toFile "module-schemas.json" (builtins.toJSON clanModuleSchemas)}
          cp "$MSCHEMA" $out
        '';

        function-schema = pkgs.runCommand "function-schema" { } ''
          FSCHEMA=${builtins.toFile "function-schemas.json" (builtins.toJSON clanModuleFunctionSchemas)}
          cp "$FSCHEMA" $out
        '';
      };
    };
}
