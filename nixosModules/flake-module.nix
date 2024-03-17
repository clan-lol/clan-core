{ inputs, self, ... }: {
  flake.nixosModules = {
    hidden-ssh-announce.imports = [ ./hidden-ssh-announce.nix ];
    installer.imports = [
      ./installer
      self.nixosModules.hidden-ssh-announce
      inputs.disko.nixosModules.disko
    ];
    clanCore.imports = [
      inputs.sops-nix.nixosModules.sops
      ./clanCore
      ./iso
      ({ pkgs, lib, ... }: {
        clanCore.clanPkgs = lib.mkDefault self.packages.${pkgs.hostPlatform.system};
      })
    ];
  };
}
