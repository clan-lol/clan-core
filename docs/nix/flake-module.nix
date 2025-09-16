{ inputs, self, ... }:
{
  imports = [
    ./options/flake-module.nix
  ];
  perSystem =
    {
      config,
      self',
      pkgs,
      ...
    }:
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
            install -D -m755 ${./render_options}/__init__.py $out/bin/render-options
            patchShebangs --build $out/bin/render-options

            ruff format --check --diff $out/bin/render-options
            ruff check --line-length 88 $out/bin/render-options
            mypy --strict $out/bin/render-options
          '';

      asciinema-player-js = pkgs.fetchurl {
        url = "https://github.com/asciinema/asciinema-player/releases/download/v3.7.0/asciinema-player.min.js";
        sha256 = "sha256-Ymco/+FinDr5YOrV72ehclpp4amrczjo5EU3jfr/zxs=";
      };
      asciinema-player-css = pkgs.fetchurl {
        url = "https://github.com/asciinema/asciinema-player/releases/download/v3.7.0/asciinema-player.css";
        sha256 = "sha256-GZMeZFFGvP5GMqqh516mjJKfQaiJ6bL38bSYOXkaohc=";
      };

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

            mkdir $out

            # The python script will place mkDocs files in the output directory
            exec python3 ${renderOptions}/bin/render-options
          '';
    in
    {
      legacyPackages = {
        inherit
          jsonDocs
          clanModulesViaService
          ;
      };
      devShells.docs = self'.packages.docs.overrideAttrs (_old: {
        nativeBuildInputs =
          self'.devShells.default.nativeBuildInputs ++ self'.packages.docs.nativeBuildInputs;
        shellHook = ''
          ${self'.devShells.default.shellHook}
          git_root=$(git rev-parse --show-toplevel)
          cd "$git_root"
          runPhase configurePhase
        '';
      });
      packages = {
        docs = pkgs.python3.pkgs.callPackage ./default.nix {
          inherit (self'.packages)
            clan-cli-docs
            docs-options
            inventory-api-docs
            clan-lib-openapi
            ;
          inherit (inputs) nixpkgs;
          inherit module-docs;
          inherit asciinema-player-js;
          inherit asciinema-player-css;
        };
        deploy-docs = pkgs.callPackage ./deploy-docs.nix { inherit (config.packages) docs; };
        inherit module-docs;
      };
    };
}
