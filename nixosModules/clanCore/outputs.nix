{
  lib,
  ...
}:
{
  # TODO: factor these out into a separate interface.nix.
  # Also think about moving these options out of `system.clan`.
  # Maybe we should not re-use the already polluted config.system namespace
  #   and instead have a separate top-level namespace like `clanOutputs`, with
  #   well defined options marked as `internal = true;`.
  options.system.clan = lib.mkOption {
    default = { };
    type = lib.types.submodule {
      options = {
        deployment.nixosMobileWorkaround = lib.mkOption {
          type = lib.types.bool;
          description = ''
            if true, the deployment will first do a nixos-rebuild switch
            to register the boot profile the command will fail applying it to the running system
            which is why afterwards we execute a nixos-rebuild test to apply
            the new config without having to reboot.
            This is a nixos-mobile deployment bug and will be removed in the future
          '';
          default = false;
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
}
