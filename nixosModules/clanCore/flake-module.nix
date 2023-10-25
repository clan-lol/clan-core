{ self, inputs, lib, ... }: {
  flake.nixosModules.clanCore = { config, pkgs, options, ... }: {
    imports = [
      ../clanImports
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
    # TODO: factor these out into a separate interface.nix.
    # Also think about moving these options out of `system.clan`.
    # Maybe we should not re-use the already polluted confg.system namespace
    #   and instead have a separate top-level namespace like `clanOutputs`, with
    #   well defined options marked as `internal = true;`.
    options.system.clan = lib.mkOption {
      type = lib.types.submodule {
        options = {
          deployment.data = lib.mkOption {
            type = lib.types.attrs;
            description = ''
              the data to be written to the deployment.json file
            '';
          };
          deployment.file = lib.mkOption {
            type = lib.types.path;
            description = ''
              the location of the deployment.json file
            '';
          };
          deploymentAddress = lib.mkOption {
            type = lib.types.str;
            description = ''
              the address of the deployment server
            '';
          };
          secretsUploadDirectory = lib.mkOption {
            type = lib.types.path;
            description = ''
              the directory on the deployment server where secrets are uploaded
            '';
          };
          uploadSecrets = lib.mkOption {
            type = lib.types.path;
            description = ''
              script to upload secrets to the deployment server
            '';
            default = "${pkgs.coreutils}/bin/true";
          };
          generateSecrets = lib.mkOption {
            type = lib.types.path;
            description = ''
              script to generate secrets
            '';
            default = "${pkgs.coreutils}/bin/true";
          };
          vm.config = lib.mkOption {
            type = lib.types.attrs;
            description = ''
              the vm config
            '';
          };
          vm.create = lib.mkOption {
            type = lib.types.path;
            description = ''
              json metadata about the vm
            '';
          };
        };
      };
      description = ''
        utility outputs for clan management of this machine
      '';
    };
    # optimization for faster secret generate/upload and machines update
    config = {
      system.clan.deployment.data = {
        inherit (config.system.clan) uploadSecrets generateSecrets;
        inherit (config.clan.networking) deploymentAddress;
        inherit (config.clanCore) secretsUploadDirectory;
      };
      system.clan.deployment.file = pkgs.writeText "deployment.json" (builtins.toJSON config.system.clan.deployment.data);
    };
  };
}
