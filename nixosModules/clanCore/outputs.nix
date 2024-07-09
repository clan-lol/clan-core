{
  config,
  lib,
  pkgs,
  ...
}:
{
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
          type = lib.types.nullOr lib.types.str;
          description = ''
            the hostname of the build host where nixos-rebuild is run
          '';
        };
        deployment.targetHost = lib.mkOption {
          type = lib.types.nullOr lib.types.str;
          description = ''
            the hostname of the target host to be deployed to
          '';
        };
        deployment.requireExplicitUpdate = lib.mkOption {
          type = lib.types.bool;
          description = ''
            if true, the deployment will not be updated automatically.
          '';
          default = false;
        };
        vm.create = lib.mkOption {
          type = lib.types.path;
          description = ''
            json metadata about the vm
          '';
        };
        iso = lib.mkOption {
          type = lib.types.path;
          description = ''
            A generated iso of the machine for the flash command
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
      facts = {
        inherit (config.clan.core.facts)
          secretUploadDirectory
          secretModule
          publicModule
          services
          ;
      };
      inherit (config.clan.core.networking) targetHost buildHost;
      inherit (config.clan.deployment) requireExplicitUpdate;
    };
    system.clan.deployment.file = pkgs.writeText "deployment.json" (
      builtins.toJSON config.system.clan.deployment.data
    );
  };
}
