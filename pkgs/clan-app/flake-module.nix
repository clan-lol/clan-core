{
  perSystem =
    {
      lib,
      self',
      pkgs,
      config,
      ...
    }:
    {
      packages =
        {
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

        }
        //
        # todo add darwin support
        (lib.optionalAttrs pkgs.stdenv.hostPlatform.isLinux {
          clan-app-ui-storybook = self'.packages.clan-app-ui.storybook;
        });

      devShells.clan-app = pkgs.callPackage ./shell.nix {
        inherit self';
        inherit (self'.packages) clan-app webview-lib clan-app-ui;
        inherit (config.packages) clan-ts-api;
      };

      checks = config.packages.clan-app.tests;
    };
}
