{
  _class,
  config,
  options,
  lib,
  pkgs,
  ...
}:
let
  secretLocation = config.clan.core.vars.age.secretLocation;
  externalStore = config.clan.core.vars.settings.age.externalStore;
  clanDir = config.clan.core.settings.directory;
  isNixOS = _class == "nixos";
  isDarwin = _class == "darwin";

  # Path layouts: ./age-source-path.nix, ./age-runtime-path.nix.
  encryptedSourcePath = import ./age-source-path.nix;
  encryptedRuntimePath = import ./age-runtime-path.nix;

  # Internal store (default): the .age file is part of the flake and thus of
  # the system closure; secrets missing from the flake are skipped at eval
  # time (src = null).
  # External store (vars.settings.age.externalStore): the store is not in the
  # flake; populate_dir uploads the .age files next to the machine key and we
  # decrypt them from under secretLocation at runtime.
  encryptedSecretSource =
    rel_dir: fileName:
    if externalStore then
      encryptedRuntimePath secretLocation rel_dir fileName
    else
      let
        storePath = encryptedSourcePath clanDir rel_dir fileName;
      in
      if builtins.pathExists storePath then storePath else null;

  # Collect all secret files with their permissions, grouped by phase
  secretFiles = lib.concatLists (
    lib.mapAttrsToList (
      genName: gen:
      lib.concatLists (
        lib.mapAttrsToList (
          fileName: file:
          let
            src = encryptedSecretSource file.rel_dir fileName;
          in
          lib.optional (file.secret && file.deploy && src != null) {
            inherit genName fileName src;
            inherit (file)
              rel_dir
              owner
              group
              mode
              neededFor
              ;
          }
        ) gen.files
      )
    ) config.clan.core.vars.generators
  );

  # Generate a bash snippet that decrypts and sets permissions for files of a given phase.
  # Internal store: sources come from the nix store, existence is checked at
  # eval time. External store: sources come from the uploaded copy under
  # secretLocation, which may be missing at runtime, so guard and warn.
  phaseDecryptSnippet =
    phase: targetDir:
    let
      phaseFiles = lib.filter (f: f.neededFor == phase) secretFiles;
    in
    lib.concatMapStringsSep "\n" (
      f:
      let
        destFile = "${targetDir}/${f.rel_dir}/${f.fileName}";
        destDir = "${targetDir}/${f.rel_dir}";
      in
      ''
        mkdir -p "${destDir}"
      ''
      + (
        if externalStore then
          ''
            if [ -e "${f.src}" ]; then
              age --decrypt -i "$key" -o "${destFile}" "${f.src}"
              chmod ${f.mode} "${destFile}"
              chown ${f.owner}:${f.group} "${destFile}"
            else
              echo "WARNING: encrypted secret ${f.src} not found, skipping" >&2
            fi
          ''
        else
          ''
            age --decrypt -i "$key" -o "${destFile}" "${f.src}"
            chmod ${f.mode} "${destFile}"
            chown ${f.owner}:${f.group} "${destFile}"
          ''
      )
    ) phaseFiles;

  # Cross-platform secret filesystem setup.
  # Linux: ramfs (secrets never touch disk, no swap)
  # macOS: hdiutil RAM disk with HFS (closest equivalent)
  mountSecretFs = pkgs.writeShellApplication {
    name = "mount-secret-fs";
    runtimeInputs = [ pkgs.coreutils ];
    text = ''
      set -efu -o pipefail
      target="$1"
      mkdir -p "$target"

      case "$(uname)" in
        Linux)
          if ! mountpoint -q "$target"; then
            mount -t ramfs -o mode=0751,nodev,nosuid,noexec ramfs "$target"
          fi
          ;;
        Darwin)
          # Check if already mounted (marker file)
          if [ -f "$target/.age-secretfs" ]; then
            exit 0
          fi
          # 64MB RAM disk: size in 512-byte sectors
          numsectors=$(( 64 * 1024 * 1024 / 512 ))
          diskpath=$(hdiutil attach -nomount "ram://$numsectors" | tr -d '[:space:]')
          newfs_hfs -s "$diskpath"
          mount -t hfs -o nobrowse,nodev,nosuid,-m=0751 "$diskpath" "$target"
          # Marker so we know it's already set up
          touch "$target/.age-secretfs"
          ;;
        *)
          echo "Unsupported OS: $(uname)" >&2
          exit 1
          ;;
      esac

      chmod 751 "$target"
    '';
  };

  decryptAgeSecrets = pkgs.writeShellApplication {
    name = "decrypt-age-secrets";
    # $key and $effective_target may appear unused when no secrets exist
    # for a given phase, since phaseDecryptSnippet generates empty content.
    excludeShellChecks = [ "SC2034" ];
    runtimeInputs = [
      pkgs.age
      pkgs.coreutils
      mountSecretFs
    ]
    ++ lib.optionals isNixOS [
      pkgs.util-linux
    ];
    text = ''
      set -efu -o pipefail

      key="$1"       # path to age key file (key.txt)
      target="$2"    # target mount point (e.g. /run/secrets)
      phase="$3"     # phase name (e.g. "services", "users")

    ''
    + (
      if isNixOS then
        ''
          # NixOS: atomic mount replacement via `mount --bind --beneath`
          mkdir -p "$target".tmp "$target"
          if mountpoint -q "$target"; then
            mount-secret-fs "$target".tmp
          else
            mount-secret-fs "$target"
            ln -sfn "$target" "$target".tmp || true
          fi

          if mountpoint -q "$target".tmp && [ "$target".tmp != "$target" ]; then
            effective_target="$target".tmp
          else
            effective_target="$target"
          fi
        ''
      else
        ''
          # Darwin: simple RAM disk mount
          mount-secret-fs "$target"
          effective_target="$target"
        ''
    )
    + ''

      # Decrypt and set permissions (generated from Nix, sources from nix store)
      case "$phase" in
        users)
          ${phaseDecryptSnippet "users" "$effective_target"}
          ;;
        services)
          ${phaseDecryptSnippet "services" "$effective_target"}
          ;;
      esac

    ''
    + lib.optionalString isNixOS ''
      # If we used .tmp, atomically bind it beneath the old mount, then
      # unmount the old top. `mount --bind --beneath` requires util-linux
      # >= 2.40 and avoids the stacked-mount accumulation that a plain
      # `--move` would produce on shared subtrees.
      if mountpoint -q "$target".tmp && [ "$(stat -c %d "$target".tmp)" != "$(stat -c %d "$target")" ]; then
        mount --bind --beneath "$target".tmp "$target"
        umount --lazy "$target"
        umount "$target".tmp
        rmdir "$target".tmp 2>/dev/null || true
      fi
    '';
  };

  useSystemdActivation =
    isNixOS
    && (
      (options.systemd ? sysusers && config.systemd.sysusers.enable)
      || (options.services ? userborn && config.services.userborn.enable)
    );

  normalSecrets = lib.any (
    gen: lib.any (file: file.neededFor == "services") (lib.attrValues gen.files)
  ) (lib.attrValues config.clan.core.vars.generators);
  userSecrets = lib.any (gen: lib.any (file: file.neededFor == "users") (lib.attrValues gen.files)) (
    lib.attrValues config.clan.core.vars.generators
  );

  keyFile = "${secretLocation}/key.txt";
in
{
  options.clan.core.vars.age = {
    secretLocation = lib.mkOption {
      type = lib.types.path;
      default = "/etc/secret-vars";
      description = ''
        Location where the age machine key is uploaded to.
      '';
    };
  };

  config = {
    clan.core.vars.settings.fileModule =
      lib.mkIf (config.clan.core.vars.settings.secretStore == "age")
        (
          file:
          lib.mkIf file.config.secret {
            path =
              if file.config.neededFor == "users" then
                "/run/user-secrets/${file.config.rel_dir}/${file.config.name}"
              else if file.config.neededFor == "services" then
                "/run/secrets/${file.config.rel_dir}/${file.config.name}"
              else if file.config.neededFor == "activation" then
                "${secretLocation}/activation/${file.config.rel_dir}/${file.config.name}"
              else if file.config.neededFor == "partitioning" then
                "/run/partitioning-secrets/${file.config.rel_dir}/${file.config.name}"
              else
                throw "unknown neededFor ${file.config.neededFor}";
          }
        );
  }
  # ── NixOS: activation scripts ──────────────────────────────────────
  // lib.optionalAttrs isNixOS {
    system.activationScripts =
      lib.mkIf ((config.clan.core.vars.settings.secretStore == "age") && !useSystemdActivation)
        {
          setupUserSecrets = lib.mkIf userSecrets (
            lib.stringAfter
              [
                "specialfs"
              ]
              ''
                [ -e /run/current-system ] || echo setting up age user secrets...
                ${decryptAgeSecrets}/bin/decrypt-age-secrets \
                  "${keyFile}" \
                  /run/user-secrets \
                  users
              ''
            // lib.optionalAttrs (config.system ? dryActivationScript) {
              supportsDryActivation = true;
            }
          );
          users.deps = lib.mkIf userSecrets [ "setupUserSecrets" ];
          setupSecrets = lib.mkIf normalSecrets (
            lib.stringAfter
              [
                "specialfs"
                "users"
                "groups"
              ]
              ''
                [ -e /run/current-system ] || echo setting up age secrets...
                ${decryptAgeSecrets}/bin/decrypt-age-secrets \
                  "${keyFile}" \
                  /run/secrets \
                  services
              ''
            // lib.optionalAttrs (config.system ? dryActivationScript) {
              supportsDryActivation = true;
            }
          );
        };

    # ── NixOS: systemd services (sysusers/userborn) ────────────────────
    systemd.services =
      lib.mkIf ((config.clan.core.vars.settings.secretStore == "age") && useSystemdActivation)
        {
          age-decrypt-user-secrets = lib.mkIf userSecrets {
            wantedBy = [ "systemd-sysusers.service" ];
            before = [ "systemd-sysusers.service" ];
            unitConfig.DefaultDependencies = "no";

            serviceConfig = {
              Type = "oneshot";
              ExecStart = [
                "${decryptAgeSecrets}/bin/decrypt-age-secrets ${keyFile} /run/user-secrets users"
              ];
              RemainAfterExit = true;
            };
          };
          age-decrypt-secrets = lib.mkIf normalSecrets {
            wantedBy = [ "sysinit.target" ];
            after = [ "systemd-sysusers.service" ];
            unitConfig.DefaultDependencies = "no";

            serviceConfig = {
              Type = "oneshot";
              ExecStart = [
                "${decryptAgeSecrets}/bin/decrypt-age-secrets ${keyFile} /run/secrets services"
              ];
              RemainAfterExit = true;
            };
          };
        };
  }
  # ── Darwin: launchd + activation ───────────────────────────────────
  // lib.optionalAttrs isDarwin {
    launchd.daemons = lib.mkIf (config.clan.core.vars.settings.secretStore == "age") {
      age-decrypt-secrets = lib.mkIf normalSecrets {
        command = "${decryptAgeSecrets}/bin/decrypt-age-secrets ${keyFile} /run/secrets services";
        serviceConfig = {
          RunAtLoad = true;
          KeepAlive = false;
        };
      };
    };
  };
}
