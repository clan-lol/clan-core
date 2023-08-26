{
  inputs = {
    # this placeholder is replaced by the path to nixpkgs
    nixpkgs.url = "__CLAN_NIXPKGS__";
  };

  outputs = _inputs: {
    clanModules.machine-machine1 = ./clanModules/machine1.nix;
  };
}
