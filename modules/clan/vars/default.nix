{ lib, ... }:
{
  options.settings = lib.mkOption {
    type = lib.types.deferredModuleWith {
      staticModules = [ ./settings-opts.nix ];
    };
    default = { };
  };
}
