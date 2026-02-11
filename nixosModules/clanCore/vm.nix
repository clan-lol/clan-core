{
  lib,
  config,
  pkgs,
  options,
  extendModules,
  ...
}:
let
  # Import the standalone VM base module
  vmModule = import ./vm-base.nix;

  # We cannot simply merge the VM config into the current system config, because
  # it is not necessarily a VM.
  # Instead we use extendModules to create a second instance of the current
  # system configuration, and then merge the VM config into that.
  vmConfig = extendModules { modules = [ vmModule ]; };
in
{
  _class = "nixos";

  options = {
    clan.virtualisation = {
      cores = lib.mkOption {
        type = lib.types.ints.positive;
        default = 1;
        description = ''
          Specify the number of cores the guest is permitted to use.
          The number can be higher than the available cores on the
          host system.
        '';
      };

      memorySize = lib.mkOption {
        type = lib.types.ints.positive;
        default = 1024;
        description = ''
          The memory size in megabytes of the virtual machine.
        '';
      };

      graphics = lib.mkOption {
        type = lib.types.bool;
        default = true;
        description = ''
          Whether to run QEMU with a graphics window, or in nographic mode.
          Serial console will be enabled on both settings, but this will
          change the preferred console.
        '';
      };

      waypipe = {
        enable = lib.mkOption {
          type = lib.types.bool;
          default = false;
          description = ''
            Whether to use waypipe for native wayland passthrough, or not.
          '';
        };
        command = lib.mkOption {
          type = lib.types.listOf lib.types.str;
          default = [ ];
          description = "Commands that waypipe should run";
        };
      };
    };
  };

  config = {
    # for clan vm create
    system.clan.vm = {
      create = pkgs.writeText "vm.json" (
        builtins.toJSON {
          initrd = "${vmConfig.config.system.build.initialRamdisk}/${vmConfig.config.system.boot.loader.initrdFile}";
          toplevel = vmConfig.config.system.build.toplevel;
          regInfo = (pkgs.closureInfo { rootPaths = vmConfig.config.virtualisation.additionalPaths; });
          inherit (config.clan.virtualisation)
            memorySize
            cores
            graphics
            waypipe
            ;
        }
      );
    };

    virtualisation = lib.optionalAttrs (options.virtualisation ? cores) {
      memorySize = lib.mkDefault config.clan.virtualisation.memorySize;
      graphics = lib.mkDefault config.clan.virtualisation.graphics;
      cores = lib.mkDefault config.clan.virtualisation.cores;
    };
  };
}
