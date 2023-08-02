{ self, lib, ... }:
let
  installer = lib.nixosSystem {
    system = "x86_64-linux";
    modules = [
      self.nixosModules.installer
      self.nixosModules.hidden-ssh-announce
      self.inputs.nixos-generators.nixosModules.all-formats
      self.inputs.disko.nixosModules.disko
      ({ config, ... }: { system.stateVersion = config.system.nixos.version; })
    ];
  };
in
{
  flake.packages.x86_64-linux.install-iso = self.inputs.disko.lib.lib.makeDiskImage { nixosConfig = installer; };
  flake.apps.x86_64-linux.install-vm.program = installer.config.formats.vm.outPath;
  flake.apps.x86_64-linux.install-vm-nogui.program = installer.config.formats.vm-nogui.outPath;
}
