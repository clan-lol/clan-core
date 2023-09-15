{
  # this placeholder is replaced by the path to nixpkgs
  inputs.nixpkgs.url = "__NIXPKGS__";

  outputs = inputs: {
    nixosConfigurations.machine1 = inputs.nixpkgs.lib.nixosSystem {
      modules = [
        ./nixosModules/machine1.nix
        (if builtins.pathExists ./machines/machine1.json
        then builtins.fromJSON (builtins.readFile ./machines/machine1.json)
        else { })
        {
          nixpkgs.hostPlatform = "x86_64-linux";
          # speed up by not instantiating nixpkgs twice and disable documentation
          nixpkgs.pkgs = inputs.nixpkgs.legacyPackages.x86_64-linux;
          documentation.enable = false;
        }
      ];
    };
  };
}
