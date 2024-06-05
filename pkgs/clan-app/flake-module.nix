{ ... }:
{
  perSystem =
    {
      config,
      pkgs,
      lib,
      system,
      ...
    }:
    if lib.elem system lib.platforms.darwin then
      { }
    else
      {
        devShells.clan-app = pkgs.callPackage ./shell.nix {
          inherit (config.packages) clan-app webview-ui;
        };
        packages.clan-app = pkgs.python3.pkgs.callPackage ./default.nix {
          inherit (config.packages) clan-cli webview-ui;
        };

        checks = config.packages.clan-app.tests;
      };
}
