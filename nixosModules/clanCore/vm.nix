{ lib, config, pkgs, options, extendModules, modulesPath, ... }:
let
  vmConfig = extendModules {
    modules = [
      (modulesPath + "/virtualisation/qemu-vm.nix")
    ];
  };
in
{
  options = {
    clan.virtualisation = {
      cores = lib.mkOption {
        type = lib.types.ints.positive;
        default = 1;
        description = lib.mdDoc ''
          Specify the number of cores the guest is permitted to use.
          The number can be higher than the available cores on the
          host system.
        '';
      };

      memorySize = lib.mkOption {
        type = lib.types.ints.positive;
        default = 1024;
        description = lib.mdDoc ''
          The memory size in megabytes of the virtual machine.
        '';
      };

      graphics = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = lib.mdDoc ''
          Whether to run QEMU with a graphics window, or in nographic mode.
          Serial console will be enabled on both settings, but this will
          change the preferred console.
        '';
      };
    };
  };

  config = {
    system.clan.vm = {
      # for clan vm inspect
      config = {
        inherit (config.clan.virtualisation) cores graphics;
        memory_size = config.clan.virtualisation.memorySize;
      };
      # for clan vm create
      create = pkgs.writeText "vm.json" (builtins.toJSON {
        initrd = "${vmConfig.config.system.build.initialRamdisk}/${vmConfig.config.system.boot.loader.initrdFile}";
        toplevel = vmConfig.config.system.build.toplevel;
        regInfo = (pkgs.closureInfo { rootPaths = vmConfig.config.virtualisation.additionalPaths; });
        inherit (config.clan.virtualisation) memorySize cores graphics;
      });
    };

    virtualisation = lib.optionalAttrs (options.virtualisation ? cores) {
      memorySize = lib.mkDefault config.clan.virtualisation.memorySize;
      graphics = lib.mkDefault config.clan.virtualisation.graphics;
      cores = lib.mkDefault config.clan.virtualisation.cores;
    };
  };
}
