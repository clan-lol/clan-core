{ inputs, self, ... }: {
  flake.nixosModules = {
    hidden-ssh-announce.imports = [ ./hidden-ssh-announce.nix ];
    installer.imports = [ ./installer ];
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
