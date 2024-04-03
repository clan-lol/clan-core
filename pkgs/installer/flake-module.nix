{ self, lib, ... }:
let
  installerModule =
    { config, pkgs, ... }:
    {
      imports = [
        self.nixosModules.installer
        self.inputs.nixos-generators.nixosModules.all-formats
      ];

      system.stateVersion = config.system.nixos.version;
      nixpkgs.pkgs = self.inputs.nixpkgs.legacyPackages.x86_64-linux;
    };

  installer = lib.nixosSystem {
    modules = [
      installerModule
      { disko.memSize = 4096; } # FIXME: otherwise the image builder goes OOM
    ];
  };
in
{
  flake.packages.x86_64-linux.install-iso = self.inputs.disko.lib.makeDiskImages {
    nixosConfig = installer;
  };

  clan = {
    clanName = "clan-core";
    directory = self;
    machines.installer = {
      imports = [ installerModule ];
      fileSystems."/".device = lib.mkDefault "/dev/null";
      boot.loader.grub.device = lib.mkDefault "/dev/null";
    };
  };
  flake.apps.x86_64-linux.install-vm.program = installer.config.formats.vm.outPath;
  flake.apps.x86_64-linux.install-vm-nogui.program = installer.config.formats.vm-nogui.outPath;
}
