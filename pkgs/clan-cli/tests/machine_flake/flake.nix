{
  inputs = {
    # this placeholder is replaced by the path to nixpkgs
    nixpkgs.url = "__NIXPKGS__";
  };

  outputs = _inputs: {
    clanModules.machine-machine1 = ./clanModules/machine1.nix;
  };
}
