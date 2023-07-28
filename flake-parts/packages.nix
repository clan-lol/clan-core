{ self, lib, ... }: {
  flake.packages.x86_64-linux =
    let
      installer = lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          self.nixosModules.installer
          self.inputs.nixos-generators.nixosModules.all-formats
          self.inputs.disko.nixosModules.disko
        ];
      };
    in
    {
      install-iso = self.inputs.disko.lib.lib.makeDiskImage { nixosConfig = installer; };
      install-vm-nogui = installer.config.formats.vm-nogui;
      install-vm = installer.config.formats.vm;
    };
}
