{ inputs, ... }: {
  flake.nixosModules = {
    hidden-ssh-announce.imports = [ ./hidden-ssh-announce.nix ];
    installer.imports = [ ./installer ];
    secrets.imports = [
      inputs.sops-nix.nixosModules.sops
      ./secrets
    ];
  };
}
