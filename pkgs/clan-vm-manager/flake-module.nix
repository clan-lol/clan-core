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
    {
      devShells.clan-vm-manager = pkgs.callPackage ./shell.nix {
        inherit (config.packages) clan-vm-manager;
      };
    }
    // lib.optionalAttrs (system != lib.platforms.darwin) {
      packages.clan-vm-manager = pkgs.python3.pkgs.callPackage ./default.nix {
        inherit (config.packages) clan-cli;
      };

      checks = config.packages.clan-vm-manager.tests;
    };
}
