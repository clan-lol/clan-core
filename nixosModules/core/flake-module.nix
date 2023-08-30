{ self, inputs, lib, ... }: {
  flake.nixosModules.clan.core = { pkgs, ... }: {
    options.clan.core = {
      clanDir = lib.mkOption {
        type = lib.types.str;
        description = ''
          the location of the flake repo, used to calculate the location of facts and secrets
        '';
      };
      machineName = lib.mkOption {
        type = lib.types.str;
        description = ''
          the name of the machine
        '';
      };
      clanPkgs = lib.mkOption {
        default = self.packages.${pkgs.system};
      };
    };
    options.system.clan = lib.mkOption {
      type = lib.types.lazyAttrsOf lib.types.raw;
      description = ''
        utility outputs for clan management of this machine
      '';
    };
    imports = [
      ./secrets
      ./zerotier.nix
      inputs.sops-nix.nixosModules.sops
    ];
  };
}
