{
  self,
  config,
  inputs,
  privateInputs ? { },
  ...
}:
{
  perSystem =
    {
      lib,
      pkgs,
      ...
    }:
    let
      inherit (lib)
        mapAttrsToList
        flip
        mapAttrs
        mkOption
        types
        splitString
        stringLength
        substring
        ;
      inherit (self) clanLib;

      serviceModules = self.clan.modules;

      baseHref = "/options-page/";

      getRoles =
        module:
        (clanLib.evalService {
          modules = [ module ];
          prefix = [ ];
        }).config.roles;

      getManifest =
        module:
        (clanLib.evalService {
          modules = [ module ];
          prefix = [ ];
        }).config.manifest;

      loadFile = file: if builtins.pathExists file then builtins.readFile file else "";

      settingsModules =
        module: flip mapAttrs (getRoles module) (_roleName: roleConfig: roleConfig.interface);

      # Map each letter to its capitalized version
      capitalizeChar =
        char:
        {
          a = "A";
          b = "B";
          c = "C";
          d = "D";
          e = "E";
          f = "F";
          g = "G";
          h = "H";
          i = "I";
          j = "J";
          k = "K";
          l = "L";
          m = "M";
          n = "N";
          o = "O";
          p = "P";
          q = "Q";
          r = "R";
          s = "S";
          t = "T";
          u = "U";
          v = "V";
          w = "W";
          x = "X";
          y = "Y";
          z = "Z";
        }
        .${char};

      title =
        name:
        let
          # split by -
          parts = splitString "-" name;
          # capitalize first letter of each part
          capitalize = part: (capitalizeChar (substring 0 1 part)) + substring 1 (stringLength part) part;
          capitalizedParts = map capitalize parts;
        in
        builtins.concatStringsSep " " capitalizedParts;

      fakeInstanceOptions =
        name: module:
        let
          manifest = getManifest module;
          description = ''
            # ${title name} (Clan Service)

            **${manifest.description}**

            ${loadFile (module._file + "/../README.md")}

            ${
              if manifest.categories != [ ] then
                "Categories: " + builtins.concatStringsSep ", " manifest.categories
              else
                "No categories defined"
            }

          '';
        in
        {
          options = {
            _ = mkOption {
              type = types.raw;
            };
            instances.${name} = lib.mkOption {
              inherit description;
              type = types.submodule {
                options.roles = flip mapAttrs (settingsModules module) (
                  roleName: roleSettingsModule:
                  mkOption {
                    type = types.submodule {
                      _file = "docs flake-module";
                      imports = [
                        { _module.args = { inherit clanLib; }; }
                        (import ../../../lib/modules/inventoryClass/roles-interface.nix {
                          nestedSettingsOption = mkOption {
                            type = types.raw;
                            description = ''
                              See [instances.${name}.roles.${roleName}.settings](${baseHref}?option_scope=0&option=instances.${name}.roles.${roleName}.settings)
                            '';
                          };
                          settingsOption = mkOption {
                            type = types.submoduleWith {
                              modules = [ roleSettingsModule ];
                            };
                          };
                        })
                      ];
                    };
                  }
                );
              };
            };
          };
        };

      mkScope = name: modules: {
        inherit name;
        modules = [
          {
            _module.args = { inherit clanLib; };
            _file = "docs mkScope";
          }
          { noInstanceOptions = true; }
          ../../../lib/modules/inventoryClass/interface.nix
        ] ++ mapAttrsToList fakeInstanceOptions modules;
        urlPrefix = "https://github.com/nix-community/dream2nix/blob/main/";
      };
    in
    {
      packages = lib.optionalAttrs ((privateInputs ? nuschtos) || (inputs ? nuschtos)) {
        docs-options =
          (privateInputs.nuschtos or inputs.nuschtos)
          .packages.${pkgs.stdenv.hostPlatform.system}.mkMultiSearch
            {
              inherit baseHref;
              title = "Clan Options";
              # scopes = mapAttrsToList mkScope serviceModules;
              scopes = [ (mkScope "Clan Inventory" serviceModules) ];
            };
      };
    };
}
