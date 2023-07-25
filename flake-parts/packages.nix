{ self, lib, ... }: {
  flake.packages.x86_64-linux =
    let
      installer = lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          self.nixosModules.installer
          self.inputs.nixos-generators.nixosModules.all-formats
        ];
      };
    in
    {
      install-iso = installer.config.formats.install-iso;
      install-vm-nogui = installer.config.formats.vm-nogui;
      install-vm = installer.config.formats.vm;
    };
}
