{
  imports = [
    ./webview-ui/flake-module.nix
  ];

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
        inherit (self'.packages) clan-app webview-lib webview-ui;
        inherit (config.packages) clan-ts-api;
      };

      packages.clan-app = pkgs.callPackage ./default.nix {
        inherit (config.packages) clan-cli webview-ui webview-lib;
        pythonRuntime = pkgs.python3;
      };

      checks = config.packages.clan-app.tests;
    };
}
