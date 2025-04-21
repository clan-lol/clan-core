{
  lib,
  ...
}:
{
  # Add the computed tags to machine tags for displaying them
  inventory = {
    tags = (
      { machines, ... }:
      {
        # Only compute the default value
        # The option MUST be defined in ./build-inventory/interface.nix
        all = lib.mkDefault (builtins.attrNames machines);
        nixos = lib.mkDefault (
          builtins.attrNames (lib.filterAttrs (_n: m: m.machineClass == "nixos") machines)
        );
        darwin = lib.mkDefault (
          builtins.attrNames (lib.filterAttrs (_n: m: m.machineClass == "darwin") machines)
        );
      }
    );
  };
}
