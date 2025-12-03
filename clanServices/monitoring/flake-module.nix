{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.monitoring = module;
}
