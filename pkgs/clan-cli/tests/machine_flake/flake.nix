{
  inputs = {
    # this placeholder is replaced by the path to nixpkgs
    nixpkgs.url = "__NIXPKGS__";
  };

  outputs = _inputs: {
    nixosModules.machine-machine1 = ./nixosModules/machine1.nix;
  };
}
