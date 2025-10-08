{ self, inputs, ... }:
{
  perSystem =
    { pkgs, self', ... }:
    let
      # Simply evaluated options (JSON)
      # { clanCore = «derivation JSON»; clanModules = { ${name} = «derivation JSON» }; }
      jsonDocs = pkgs.callPackage ./get-module-docs.nix {
        inherit (self) clanModules;
        clan-core = self;
        inherit pkgs;
      };

      # clan service options
      clanModulesViaService = pkgs.writeText "info.json" (builtins.toJSON jsonDocs.clanModulesViaService);

      # Simply evaluated options (JSON)
      renderOptions =
        pkgs.runCommand "render-options"
          {
            # TODO: ruff does not splice properly in nativeBuildInputs
            depsBuildBuild = [ pkgs.ruff ];
            nativeBuildInputs = [
              pkgs.python3
              pkgs.mypy
              self'.packages.clan-cli
            ];
          }
          ''
            install -D -m755 ${./generate}/__init__.py $out/bin/render-options
            patchShebangs --build $out/bin/render-options

            ruff format --check --diff $out/bin/render-options
            ruff check --line-length 88 $out/bin/render-options
            mypy --strict $out/bin/render-options
          '';

      module-docs =
        pkgs.runCommand "rendered"
          {
            buildInputs = [
              pkgs.python3
              self'.packages.clan-cli
            ];
          }
          ''
            export CLAN_CORE_PATH=${
              inputs.nixpkgs.lib.fileset.toSource {
                root = ../..;
                fileset = ../../clanModules;
              }
            }
            export CLAN_CORE_DOCS=${jsonDocs.clanCore}/share/doc/nixos/options.json

            # A file that contains the links to all clanModule docs
            export CLAN_MODULES_VIA_SERVICE=${clanModulesViaService}
            export CLAN_SERVICE_INTERFACE=${self'.legacyPackages.clan-service-module-interface}/share/doc/nixos/options.json
            export CLAN_OPTIONS_PATH=${self'.legacyPackages.clan-options}/share/doc/nixos/options.json

            mkdir $out

            # The python script will place mkDocs files in the output directory
            exec python3 ${renderOptions}/bin/render-options
          '';
    in
    {
      packages = {
        inherit module-docs;
      };
    };
}
