{ ... }:
let
  module = ./default.nix;
in
{
  clan.modules.dm-dns = module;
}
