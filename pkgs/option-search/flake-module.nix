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

      baseHref = "/option-search/";

      # Map each letter to its capitalized version

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
        option-search =
          if privateInputs ? nuschtos then
            privateInputs.nuschtos.packages.${pkgs.stdenv.hostPlatform.system}.mkMultiSearch {
              inherit baseHref;
              title = "Clan Options";
              # scopes = mapAttrsToList mkScope serviceModules;
              scopes = [
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
