{
  imports = [
    ./clan-app/flake-module.nix
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

      devShells.ui = pkgs.callPackage ./shell.nix {
        inherit self';
        inherit (self'.packages) clan-app webview-lib webview-ui;
        inherit (config.packages) clan-ts-api;
      };
    };
}
