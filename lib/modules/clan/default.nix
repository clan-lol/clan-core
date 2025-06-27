{ clan-core }:
{
  _class = "clan";
  _module.args = {
    inherit clan-core;
    inherit (clan-core) clanLib;
  };
  imports = [
    ./module.nix
    ./interface.nix
  ];
}
