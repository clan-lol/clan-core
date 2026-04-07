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
      imports = [
        ./clanCore
        inputs.sops-nix."${_class}Modules".sops
      ]
      ++ lib.optionals (_class == "nixos") [
        inputs.disko.nixosModules.default
        inputs.data-mesher.nixosModules.data-mesher
      ]
      ++ lib.optionals (_class == "darwin") [
        ../darwinModules/hosts.nix
      ];
      config = {
        clan.core.clanPkgs = lib.mkDefault {
          zerotier-members = pkgs.callPackage (self + "/pkgs/zerotier-members") { };
          zerotierone = pkgs.callPackage (self + "/pkgs/zerotierone") { };
        };
      };
    };
in
{
  flake.nixosModules.hidden-ssh-announce = ./hidden-ssh-announce.nix;
  flake.nixosModules.bcachefs = ./bcachefs.nix;
  flake.nixosModules.user-firewall = ./user-firewall;
  flake.nixosModules.installer.imports = [
    ./installer
    self.nixosModules.hidden-ssh-announce
    self.nixosModules.bcachefs
  ];

  flake.nixosModules.clanCore = clanCore;
  flake.darwinModules.clanCore = clanCore;
}
