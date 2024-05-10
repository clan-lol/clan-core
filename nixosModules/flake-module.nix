{ inputs, self, ... }:
{
  flake.nixosModules = {
    hidden-ssh-announce.imports = [ ./hidden-ssh-announce.nix ];
    installer.imports = [
      ./installer
      self.nixosModules.hidden-ssh-announce
    ];
    clanCore.imports = [
      inputs.sops-nix.nixosModules.sops
      inputs.disko.nixosModules.default
      ./clanCore
      ./iso
      (
        { pkgs, lib, ... }:
        {
          clanCore.clanPkgs = lib.mkDefault self.packages.${pkgs.hostPlatform.system};
        }
      )
    ];
  };
}
