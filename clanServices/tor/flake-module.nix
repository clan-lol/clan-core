{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    tor = module;
  };
}
