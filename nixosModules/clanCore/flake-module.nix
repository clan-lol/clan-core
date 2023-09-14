{ self, inputs, lib, ... }: {
  flake.nixosModules.clanCore = { pkgs, options, ... }: {
    imports = [
      ./secrets
      ./zerotier.nix
      ./networking.nix
      inputs.sops-nix.nixosModules.sops
      # just some example options. Can be removed later
      ./bloatware
    ];
    options.clanSchema = lib.mkOption {
      type = lib.types.attrs;
      description = "The json schema for the .clan options namespace";
      default = self.lib.jsonschema.parseOptions options.clan;
    };
    options.clanCore = {
      clanDir = lib.mkOption {
        type = lib.types.either lib.types.path lib.types.str;
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
  };
}
