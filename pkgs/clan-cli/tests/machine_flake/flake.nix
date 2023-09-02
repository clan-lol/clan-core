{
  inputs = {
    # this placeholder is replaced by the path to nixpkgs
    nixpkgs.url = "__NIXPKGS__";
  };

  outputs = inputs: {
    nixosConfigurations.machine1 = inputs.nixpkgs.lib.nixosSystem {
      modules = [
        ./nixosModules/machine1.nix
        (if builtins.pathExists ./machines/machine1.json
        then builtins.fromJSON (builtins.readFile ./machines/machine1.json)
        else { })
        { nixpkgs.hostPlatform = "x86_64-linux"; }
      ];
    };
  };
}
