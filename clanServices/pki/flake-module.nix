{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.pki = module;
}
