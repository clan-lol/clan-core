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
