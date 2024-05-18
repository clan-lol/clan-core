{ ... }:
{
  perSystem =
    { config, pkgs, ... }:
    {
      devShells.clan-vm-manager = pkgs.callPackage ./shell.nix {
        inherit (config.packages) clan-vm-manager webview-ui;
      };
      packages.clan-vm-manager = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (config.packages) clan-cli webview-ui;
      };

      checks = config.packages.clan-vm-manager.tests;
    };
}
