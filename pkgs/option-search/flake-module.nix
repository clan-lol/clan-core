{
  self,
  privateInputs,
  ...
}:
{
  perSystem =
    {
      pkgs,
      ...
    }:
    let

      baseHref = "./";

      coreOptions =
        (pkgs.nixosOptionsDoc {
          options =
            self.legacyPackages.x86_64-linux.jsonDocs.clanEval.config.nixosConfigurations.jon.options.clan.core;
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
