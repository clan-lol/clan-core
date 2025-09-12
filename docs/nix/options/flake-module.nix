{
  self,
  privateInputs,
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

      baseHref = "/options/";

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
                              See [instances.${name}.roles.${roleName}.settings](${baseHref}?option_scope=0&option=inventory.instances.${name}.roles.${roleName}.settings)
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

      docModules = [
        {
          inherit self;
        }
        self.modules.clan.default
        {
          options.inventory = lib.mkOption {
            type = types.submoduleWith {
              modules = [
                { noInstanceOptions = true; }
              ]
              ++ mapAttrsToList fakeInstanceOptions serviceModules;
            };
          };
        }
      ];

      baseModule =
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

      evalClanModules =
        let
          evaled = lib.evalModules {
            class = "nixos";
            modules = [
              baseModule
              {
                clan.core.settings.directory = self;
              }
              self.nixosModules.clanCore
            ];
          };
        in
        evaled;

      coreOptions =
        (pkgs.nixosOptionsDoc {
          options = (evalClanModules.options).clan.core or { };
          warningsAreErrors = true;
          transformOptions = self.clanLib.docs.stripStorePathsFromDeclarations;
        }).optionsJSON;

    in
    {
      # Uncomment for debugging
      # legacyPackages.docModules = lib.evalModules {
      #   modules = docModules;
      # };

      packages = {
        docs-options =
          if privateInputs ? nuschtos then
            privateInputs.nuschtos.packages.${pkgs.stdenv.hostPlatform.system}.mkMultiSearch {
              inherit baseHref;
              title = "Clan Options";
              # scopes = mapAttrsToList mkScope serviceModules;
              scopes = [
                {
                  inherit baseHref;
                  name = "Flake Options (clan.nix file)";
                  modules = docModules;
                  urlPrefix = "https://git.clan.lol/clan/clan-core/src/branch/main/";
                }
                {
                  name = "Machine Options (clan.core NixOS options)";
                  optionsJSON = "${coreOptions}/share/doc/nixos/options.json";
                  urlPrefix = "https://git.clan.lol/clan/clan-core/src/branch/main/";
                }
              ];
            }
          else
            pkgs.stdenv.mkDerivation {
              name = "empty";
              buildCommand = "echo 'This is an empty derivation' > $out";
            };
      };
    };
}
