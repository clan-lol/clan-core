{ pkgs, ... }:
{
  documentation.nixos.enable = pkgs.lib.mkDefault false;
}
