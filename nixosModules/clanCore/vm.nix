{ lib, config, pkgs, options, extendModules, modulesPath, ... }:
let
  # Flatten the list of state folders into a single list
  stateFolders = lib.flatten (
    lib.mapAttrsToList
      (_item: attrs: attrs.folders)
      config.clanCore.state
  );

  # Ensure sane mount order by topo-sorting
  sortedStateFolders =
    let
      sorted = lib.toposort lib.hasPrefix stateFolders;
    in
      sorted.result or (
        throw ''
          The state folders have a cyclic dependency.
          This is not allowed.
          The cyclic dependencies are:
            - ${lib.concatStringsSep "\n  - " sorted.loops}
        ''
      );

  vmModule = {
    imports = [
      (modulesPath + "/virtualisation/qemu-vm.nix")
      ./serial.nix
    ];

    # required for issuing shell commands via qga
    services.qemuGuest.enable = true;

    boot.initrd.systemd.enable = true;

    # currently needed for system.etc.overlay.enable
    boot.kernelPackages = pkgs.linuxPackages_latest;

    boot.initrd.systemd.storePaths = [ pkgs.util-linux pkgs.e2fsprogs ];
    # Ensures, that all state paths will be persisted across reboots
    # - Mounts the state.qcow2 disk to /vmstate.
    # - Binds directories from /vmstate/{some-path} to /{some-path}.
    boot.initrd.systemd.services.rw-etc-pre = {
      unitConfig = {
        DefaultDependencies = false;
        RequiresMountsFor = "/sysroot /dev";
      };
      wantedBy = [ "initrd.target" ];
      requiredBy = [ "rw-etc.service" ];
      before = [ "rw-etc.service" ];
      serviceConfig = {
        Type = "oneshot";
      };
      script = ''
        set -x
        mkdir -p -m 0755 \
          /sysroot/vmstate \
          /sysroot/.rw-etc \
          /sysroot/var/lib/nixos

        ${pkgs.util-linux}/bin/blkid /dev/vdb || ${pkgs.e2fsprogs}/bin/mkfs.ext4 /dev/vdb
        sync
        mount /dev/vdb /sysroot/vmstate

        mkdir -p -m 0755 /sysroot/vmstate/{.rw-etc,var/lib/nixos}
        mount --bind /sysroot/vmstate/.rw-etc /sysroot/.rw-etc
        mount --bind /sysroot/vmstate/var/lib/nixos /sysroot/var/lib/nixos

        for folder in "${lib.concatStringsSep ''" "'' sortedStateFolders}"; do
          mkdir -p -m 0755 "/sysroot/vmstate/$folder" "/sysroot/$folder"
          mount --bind "/sysroot/vmstate/$folder" "/sysroot/$folder"
        done
      '';
    };
    virtualisation.fileSystems = {
      ${config.clanCore.secretsUploadDirectory} = lib.mkForce {
        device = "secrets";
        fsType = "9p";
        neededForBoot = true;
        options = [ "trans=virtio" "version=9p2000.L" "cache=loose" ];
      };
    };
  };

  # We cannot simply merge the VM config into the current system config, because
  # it is not necessarily a VM.
  # Instead we use extendModules to create a second instance of the current
  # system configuration, and then merge the VM config into that.
  vmConfig = extendModules {
    modules = [ vmModule ];
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

      waypipe = lib.mkOption {
        type = lib.types.bool;
        default = false;
        description = lib.mdDoc ''
          Whether to use waypipe for native wayland passthrough, or not.
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
      waypipe = lib.mkOption {
        type = lib.types.bool;
        internal = true;
        readOnly = true;
        description = ''
          whether to enable native wayland window passthrough with waypipe for the vm
        '';
      };
    };
  };

  config = {
    # for clan vm inspect
    clanCore.vm.inspect = {
      clan_name = config.clanCore.clanName;
      memory_size = config.clan.virtualisation.memorySize;
      inherit (config.clan.virtualisation) cores graphics waypipe;
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
