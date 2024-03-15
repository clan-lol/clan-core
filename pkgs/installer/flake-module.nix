{ self, lib, ... }:
let
  installerModule = { config, pkgs, ... }: {
    imports = [
      self.nixosModules.installer
      self.nixosModules.hidden-ssh-announce
      self.inputs.nixos-generators.nixosModules.all-formats
      self.inputs.disko.nixosModules.disko
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

  clan = self.lib.buildClan {
    clanName = "clan-core";
    directory = self;
    machines.installer = installerModule;
  };
in
{
  flake.packages.x86_64-linux.install-iso = self.inputs.disko.lib.makeDiskImages {
    nixosConfig = installer;
  };
  flake.nixosConfigurations = { inherit (clan.nixosConfigurations) installer; };
  flake.clanInternals = clan.clanInternals;
  flake.apps.x86_64-linux.install-vm.program = installer.config.formats.vm.outPath;
  flake.apps.x86_64-linux.install-vm-nogui.program = installer.config.formats.vm-nogui.outPath;
}
