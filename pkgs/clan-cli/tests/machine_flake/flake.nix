{
  inputs = {
    # this placeholder is replaced by the path to nixpkgs
    nixpkgs.url = "__NIXPKGS__";
  };

  outputs = inputs: {
    nixosModules.machine-machine1 = ./nixosModules/machine1.nix;
    nixosConfigurations.machine1 = inputs.nixpkgs.lib.nixosSystem {
      modules = [
        inputs.self.nixosModules.machine-machine1
        (builtins.fromJSON (builtins.readFile ./machines/machine1.json))
        { nixpkgs.hostPlatform = "x86_64-linux"; }
      ];
    };
  };
}
