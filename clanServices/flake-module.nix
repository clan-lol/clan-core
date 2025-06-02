{ ... }:
{
  imports = [
    ./admin/flake-module.nix
    ./hello-world/flake-module.nix
    ./wifi/flake-module.nix
    ./borgbackup/flake-module.nix
  ];
}
