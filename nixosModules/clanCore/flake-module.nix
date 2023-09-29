{ self, inputs, lib, ... }: {
  flake.nixosModules.clanCore = { config, pkgs, options, ... }: {
    imports = [
      ./secrets
      ./zerotier
      ./networking.nix
      inputs.sops-nix.nixosModules.sops
      # just some example options. Can be removed later
      ./bloatware
      ./vm.nix
      ./options.nix
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
        defaultText = "self.packages.${pkgs.system}";
        internal = true;
      };
    };
    options.system.clan = lib.mkOption {
      type = lib.types.lazyAttrsOf lib.types.raw;
      description = ''
        utility outputs for clan management of this machine
      '';
    };
    # optimization for faster secret generate/upload and machines update
    config = {
      system.clan.deployment.text = builtins.toJSON {
        inherit (config.system.clan) uploadSecrets generateSecrets;
        inherit (config.clan.networking) deploymentAddress;
      };
      system.clan.deployment.file = pkgs.writeText "deployment.json" config.system.clan.deployment.text;
    };
  };
}
