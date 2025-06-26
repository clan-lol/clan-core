{ clan-core }:
{
  _class = "clan";
  _module.args = {
    inherit clan-core;
    inherit (clan-core) clanLib;
    # TODO: This should be set via an option otherwise it is not possible to override
    inherit (clan-core.inputs) nixpkgs nix-darwin;
  };
  imports = [
    ./module.nix
    ./interface.nix
  ];
}
