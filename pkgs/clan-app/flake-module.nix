{
  perSystem =
    {
      self',
      pkgs,
      config,
      ...
    }:
    {
      packages = {
        webview-lib = pkgs.callPackage ./webview-lib { };
      };

      devShells.clan-app = pkgs.callPackage ./shell.nix {
        inherit self';
        inherit (self'.packages) clan-app webview-lib clan-app-ui;
        inherit (config.packages) clan-ts-api;
      };

      packages.clan-app = pkgs.callPackage ./default.nix {
        inherit (config.packages) clan-cli clan-app-ui webview-lib;
        pythonRuntime = pkgs.python3;
      };

      packages.fonts = pkgs.callPackage ./fonts.nix { };

      packages.clan-app-ui = pkgs.callPackage ./ui.nix {
        clan-ts-api = config.packages.clan-ts-api;
        fonts = config.packages.fonts;
      };

      checks = config.packages.clan-app.tests;
    };
}
