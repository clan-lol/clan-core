{
  lib,
  pkgs,
  ...
}:
let
  parseAddFilesArgs = builtins.path {
    path = ../parse-add-files-args.sh;
    name = "parse-add-files-args.sh";
  };

  isoAddFilesScript = pkgs.writeShellApplication {
    name = "add-files";
    runtimeInputs = with pkgs; [
      gnutar
      xorriso
    ];
    extraShellCheckFlags = [ "-x" ];
    text = ''
      # shellcheck source=${parseAddFilesArgs}
      source ${parseAddFilesArgs}

      # If no extra paths, just copy source to output
      if [[ ''${#extra_paths[@]} -eq 0 ]]; then
        cp -- "$source_image" "$output_image"
        exit 0
      fi

      # Build directory tree from --extra-path mappings
      tmpdir=$(mktemp -d)
      staging_dir="$tmpdir/root"
      mkdir -m 755 "$staging_dir"
      tar_file=$(mktemp --suffix=.tar)
      trap 'rm -rf "$tmpdir" "$tar_file"' EXIT

      for ((i = 0; i < ''${#extra_paths[@]}; i += 2)); do
        local_src="''${extra_paths[i]}"
        target="''${extra_paths[i+1]}"

        # Strip leading slash for directory tree structure
        rel_target="''${target#/}"

        if [[ -d "$local_src" ]]; then
          mkdir -p "$staging_dir/$rel_target"
          cp -a "$local_src/." "$staging_dir/$rel_target/"
        else
          mkdir -p "$(dirname "$staging_dir/$rel_target")"
          cp -a "$local_src" "$staging_dir/$rel_target"
        fi
      done

      # Create tarball from the staging directory
      tar -cf "$tar_file" --owner=root --group=root -C "$staging_dir" .

      # Add the tarball to the ISO, preserving boot structures
      xorriso -indev "$source_image" \
        -outdev "$output_image" \
        -map "$tar_file" /extra-files.tar \
        -boot_image any replay
    '';
  };
in
{
  options.clan.core.image = {
    iso.addFilesScript = lib.mkOption {
      type = lib.types.package;
      default = isoAddFilesScript;
      defaultText = lib.literalExpression "pkgs.writeShellApplication { ... }";
      description = ''
        Script to inject extra files into an ISO image.

        Source `parse-add-files-args.sh` to get standardized argument parsing.
        After sourcing, `$source_image`, `$output_image`, and `$extra_paths`
        are available.

        Accepts the following arguments:
        - --source <path>: Path to the original built image (read-only)
        - --output <path>: Path for the modified output image
        - --extra-path <local-source> <target-path>: Repeatable, maps a local
          file or directory to a target filesystem path inside the image
      '';
    };
  };

  config = {
    # Extract extra-files.tar from ISO at boot time.
    # This runs in the initrd before switch_root, so files are available
    # at their target paths before any systemd services start.
    # tar extraction only creates new files/directories without modifying
    # permissions of existing parent directories.
    image.modules.iso =
      {
        config,
        lib,
        pkgs,
        ...
      }:
      {
        imports = [
          ./serial.nix
        ];
        config = lib.mkMerge [
          {
            # Reduce compression level to speedup build times
            isoImage.squashfsCompression = lib.mkOverride 900 "zstd -Xcompression-level 5";

            # Enable EFI boot (required for aarch64 which has no BIOS)
            isoImage.makeEfiBootable = true;

            # Enable hybrid USB boot for BIOS systems
            isoImage.makeUsbBootable = true;

            # Virtio modules so the ISO can boot in QEMU/KVM VMs
            boot.initrd.availableKernelModules = [
              "virtio_pci"
              "virtio_scsi"
              "virtio_blk"
            ];

            # Reduce grub bootloader timeout from 10 seconds to 1 second
            boot.loader.timeout = lib.mkForce 1;
          }
          # Scripted initrd: nix store is at /mnt-root/nix/store during postMountCommands
          (lib.mkIf (!config.boot.initrd.systemd.enable) {
            boot.initrd.postMountCommands = lib.mkAfter ''
              if [ -e /mnt-root/iso/extra-files.tar ]; then
                /mnt-root${lib.getExe pkgs.gnutar} --no-overwrite-dir -xf /mnt-root/iso/extra-files.tar -C /mnt-root/
              fi
            '';
          })

          # Systemd initrd: include tar and define extraction service
          (lib.mkIf config.boot.initrd.systemd.enable {
            boot.initrd.systemd.storePaths = [ (lib.getExe pkgs.gnutar) ];

            boot.initrd.systemd.services.clan-extra-files = {
              description = "Extract extra files from ISO tarball";
              wantedBy = [ "initrd-fs.target" ];
              after = [ "sysroot-iso.mount" ];
              before = [ "initrd-fs.target" ];
              unitConfig = {
                ConditionPathExists = "/sysroot/iso/extra-files.tar";
                OnFailure = "emergency.target";
              };
              serviceConfig = {
                Type = "oneshot";
                RemainAfterExit = true;
              };
              script = ''
                set -xe
                ${lib.getExe pkgs.gnutar} --no-overwrite-dir -xf /sysroot/iso/extra-files.tar -C /sysroot/
              '';
            };
          })
        ];
      };
  };
}
