{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules = {
    internet = module;
  };
}
