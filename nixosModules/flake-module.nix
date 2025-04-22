{ inputs, self, ... }:
let
  clanCore =
    {
      _class,
      pkgs,
      lib,
      ...
    }:
    {
      imports =
        [
          ./clanCore
          inputs.sops-nix."${_class}Modules".sops
        ]
        ++ lib.optionals (_class == "nixos") [
          inputs.nixos-facter-modules.nixosModules.facter
          inputs.disko.nixosModules.default
          inputs.data-mesher.nixosModules.data-mesher
        ];
      config = {
        clan.core.clanPkgs = lib.mkDefault self.packages.${pkgs.hostPlatform.system};
      };
    };
in
{
  flake.nixosModules.hidden-ssh-announce = ./hidden-ssh-announce.nix;
  flake.nixosModules.bcachefs = ./bcachefs.nix;
  flake.nixosModules.installer.imports = [
    ./installer
    self.nixosModules.hidden-ssh-announce
    self.nixosModules.bcachefs
  ];

  flake.nixosModules.clanCore = clanCore;
  flake.darwinModules.clanCore = clanCore;
}
