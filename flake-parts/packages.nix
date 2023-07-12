{self, ...}: {
  flake.packages.x86_64-linux = {
    inherit
      (self.nixosConfigurations.installer.config.formats)
      install-iso
      ;
  };
}
