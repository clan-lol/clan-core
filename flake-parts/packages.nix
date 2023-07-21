{ self, lib, ... }: {
  flake.packages.x86_64-linux = {
    install-iso = (lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        self.nixosModules.installer
        self.inputs.nixos-generators.nixosModules.all-formats
      ];
    }).config.formats.install-iso;
  };
}
