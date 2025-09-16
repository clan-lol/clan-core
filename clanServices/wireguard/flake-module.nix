{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.wireguard = module;
}
