{ lib, config, pkgs, options, extendModules, modulesPath, ... }:
let
  # Generates a fileSystems entry for bind mounting a given state folder path
  # It binds directories from /var/clanstate/{some-path} to /{some-path}.
  # As a result, all state paths will be persisted across reboots, because
  #   the state folder is mounted from the host system.
  mkBindMount = path: {
    name = path;
    value = {
      device = "/var/clanstate/${path}";
      options = [ "bind" ];
    };
  };

  # Flatten the list of state folders into a single list
  stateFolders = lib.flatten (
    lib.mapAttrsToList
      (_item: attrs: attrs.folders)
      config.clanCore.state
  );

  # A module setting up bind mounts for all state folders
  stateMounts = {
    virtualisation.fileSystems =
      lib.listToAttrs
        (map mkBindMount stateFolders);
  };

  vmModule = {
    imports = [
      (modulesPath + "/virtualisation/qemu-vm.nix")
      ./serial.nix
      stateMounts
    ];
    virtualisation.fileSystems = {
      ${config.clanCore.secretsUploadDirectory} = lib.mkForce {
        device = "secrets";
        fsType = "9p";
        neededForBoot = true;
        options = [ "trans=virtio" "version=9p2000.L" "cache=loose" ];
      };
      "/var/clanstate" = {
        device = "state";
        fsType = "9p";
        options = [ "trans=virtio" "version=9p2000.L" "cache=loose" ];
      };
    };
    boot.initrd.systemd.enable = true;
  };

  # We cannot simply merge the VM config into the current system config, because
  # it is not necessarily a VM.
  # Instead we use extendModules to create a second instance of the current
  # system configuration, and then merge the VM config into that.
  vmConfig = extendModules {
    modules = [ vmModule stateMounts ];
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
    # All important VM config variables needed by the vm runner
    # this is really just a remapping of values defined elsewhere
    # and therefore not intended to be set by the user
    clanCore.vm.inspect = {
      clan_name = lib.mkOption {
        type = lib.types.str;
        internal = true;
        readOnly = true;
        description = ''
          the name of the clan
        '';
      };
      memory_size = lib.mkOption {
        type = lib.types.int;
        internal = true;
        readOnly = true;
        description = ''
          the amount of memory to allocate to the vm
        '';
      };
      cores = lib.mkOption {
        type = lib.types.int;
        internal = true;
        readOnly = true;
        description = ''
          the number of cores to allocate to the vm
        '';
      };
      graphics = lib.mkOption {
        type = lib.types.bool;
        internal = true;
        readOnly = true;
        description = ''
          whether to enable graphics for the vm
        '';
      };
    };
  };

  config = {
    # for clan vm inspect
    clanCore.vm.inspect = {
      clan_name = config.clanCore.clanName;
      memory_size = config.clan.virtualisation.memorySize;
      inherit (config.clan.virtualisation) cores graphics;
    };
    # for clan vm create
    system.clan.vm = {
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
