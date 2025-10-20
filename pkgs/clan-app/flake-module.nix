{ lib, ... }:
{
  perSystem =
    {
      self',
      pkgs,
      config,
      system,
      ...
    }:
    {
      packages = {
        webview-lib = pkgs.callPackage ./webview-lib { };
        clan-app = pkgs.callPackage ./default.nix {
          inherit (config.packages) clan-cli clan-app-ui webview-lib;
          pythonRuntime = pkgs.python3;
        };

        fonts = pkgs.callPackage ./fonts.nix { };

        clan-app-ui = pkgs.callPackage ./ui.nix {
          clan-ts-api = config.packages.clan-ts-api;
          fonts = config.packages.fonts;
        };

      };
      #        //
      # todo add darwin support
      # todo re-enable
      # see ui.nix for an explanation of why this is disabled for now
      #        (lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
      #          clan-app-ui-storybook = self'.packages.clan-app-ui.storybook;
      #        });

      devShells.clan-app = pkgs.callPackage ./shell.nix {
        inherit self';
        inherit (self'.packages)
          clan-app
          webview-lib
          clan-app-ui
          clan-lib-openapi
          ;
        inherit (config.packages) clan-ts-api;
      };

      checks =
        config.packages.clan-app.tests
        # Clan's darwin CI is a sandbox too limiting to spawn a headless brwoser
        // lib.optionalAttrs (!lib.hasSuffix system "darwin") {
          inherit (config.packages.clan-app-ui.tests) clan-app-ui-storybook;
        };
    };
}
