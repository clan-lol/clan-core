{ ... }:
{
  imports = [
    ./admin/flake-module.nix
    ./deltachat/flake-module.nix
    ./ergochat/flake-module.nix
    ./auto-upgrade/flake-module.nix
    ./hello-world/flake-module.nix
    ./wifi/flake-module.nix
    ./borgbackup/flake-module.nix
  ];
}
