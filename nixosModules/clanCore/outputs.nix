{ config, lib, pkgs, ... }: {
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
        deployment.buildHost = lib.mkOption {
          type = lib.types.str;
          description = ''
            the hostname of the build host where nixos-rebuild is run
          '';
        };
        deployment.targetHost = lib.mkOption {
          type = lib.types.str;
          description = ''
            the hostname of the target host to be deployed to
          '';
        };
        secretsUploadDirectory = lib.mkOption {
          type = lib.types.path;
          description = ''
            the directory on the deployment server where secrets are uploaded
          '';
        };
        secretsModule = lib.mkOption {
          type = lib.types.str;
          description = ''
            the python import path to the secrets module
          '';
        };
        secretsData = lib.mkOption {
          type = lib.types.path;
          description = ''
            secret data as json for the generator
          '';
          default = pkgs.writers.writeJSON "secrets.json" (lib.mapAttrs
            (_name: secret: {
              secrets = builtins.attrNames secret.secrets;
              facts = lib.mapAttrs (_: secret: secret.path) secret.facts;
              generator = secret.generator.finalScript;
            })
            config.clanCore.secrets);
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
      inherit (config.system.clan) secretsModule secretsData;
      inherit (config.clan.networking) targetHost buildHost;
      inherit (config.clanCore) secretsUploadDirectory;
    };
    system.clan.deployment.file = pkgs.writeText "deployment.json" (builtins.toJSON config.system.clan.deployment.data);

  };
}
