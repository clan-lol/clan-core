{
  config,
  options,
  lib,
  pkgs,
  ...
}:
let
  installSecretTarball = pkgs.writeShellApplication {
    name = "install-secret-tarball";
    runtimeInputs = [
      pkgs.gnutar
      pkgs.gzip
      pkgs.move-mount-beneath
    ];
    text = ''
      set -efu -o pipefail
      set -x

      src=$1
      target=$2

      echo "installing secrets from $src to $target" >&2

      mkdir -p "$target".tmp "$target"
      if mountpoint -q "$target"; then
        # Prepare new mount with secrets
        mount -t tmpfs -o noswap tmpfs "$target".tmp
        chmod 511 "$target".tmp
        tar -xf "$src" -C "$target".tmp

        # Atomically move new mount beneath the old one, then unmount the old and .tmp
        move-mount --detached --beneath "$target".tmp "$target"
        umount --lazy "$target"
        umount -R "$target".tmp
        rmdir "$target".tmp
      else
        mount -t tmpfs -o noswap tmpfs "$target"
        chmod 511 "$target"
        tar -xf "$src" -C "$target"
      fi
    '';
  };
  useSystemdActivation =
    (options.systemd ? sysusers && config.systemd.sysusers.enable)
    || (options.services ? userborn && config.services.userborn.enable);

  normalSecrets = lib.any (
    gen: lib.any (file: file.neededFor == "services") (lib.attrValues gen.files)
  ) (lib.attrValues config.clan.core.vars.generators);
  userSecrets = lib.any (gen: lib.any (file: file.neededFor == "users") (lib.attrValues gen.files)) (
    lib.attrValues config.clan.core.vars.generators
  );

in
{
  _class = "nixos";

  options.clan.core.vars.password-store = {
    secretLocation = lib.mkOption {
      type = lib.types.path;
      default = "/etc/secret-vars";
      description = ''
        location where the tarball with the password-store secrets will be uploaded to and the manifest
      '';
    };
    passCommand = lib.mkOption {
      type = lib.types.enum [
        "pass"
        "passage"
      ];
      default = "passage";
      description = ''
        Password store command to use, must be available in PATH. E.g.
        - "pass": GPG-based password store
        - "passage": age-based password store
      '';
    };
  };
  config = {
    clan.core.vars.settings.fileModule =
      lib.mkIf (config.clan.core.vars.settings.secretStore == "password-store")
        (
          file:
          lib.mkIf file.config.secret {
            path =
              if file.config.neededFor == "users" then
                "/run/user-secrets/${file.config.generatorName}/${file.config.name}"
              else if file.config.neededFor == "services" then
                "/run/secrets/${file.config.generatorName}/${file.config.name}"
              else if file.config.neededFor == "activation" then
                "${config.clan.core.vars.password-store.secretLocation}/activation/${file.config.generatorName}/${file.config.name}"
              else if file.config.neededFor == "partitioning" then
                "/run/partitioning-secrets/${file.config.generatorName}/${file.config.name}"
              else
                throw "unknown neededFor ${file.config.neededFor}";

          }
        );
    clan.core.vars.settings.secretModule = lib.mkIf (
      config.clan.core.vars.settings.secretStore == "password-store"
    ) "clan_cli.vars.secret_modules.password_store";

    system.activationScripts =
      lib.mkIf ((config.clan.core.vars.settings.secretStore == "password-store") && !useSystemdActivation)
        {
          setupUserSecrets = lib.mkIf userSecrets (
            lib.stringAfter
              [
                "specialfs"
              ]
              ''
                [ -e /run/current-system ] || echo setting up secrets...
                ${installSecretTarball}/bin/install-secret-tarball ${config.clan.core.vars.password-store.secretLocation}/secrets_for_users.tar.gz /run/user-secrets
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
                [ -e /run/current-system ] || echo setting up secrets...
                ${installSecretTarball}/bin/install-secret-tarball ${config.clan.core.vars.password-store.secretLocation}/secrets.tar.gz /run/secrets
              ''
            // lib.optionalAttrs (config.system ? dryActivationScript) {
              supportsDryActivation = true;
            }
          );
        };
    systemd.services =
      lib.mkIf ((config.clan.core.vars.settings.secretStore == "password-store") && useSystemdActivation)
        {
          pass-install-user-secrets = lib.mkIf userSecrets {
            wantedBy = [ "systemd-sysusers.service" ];
            before = [ "systemd-sysusers.service" ];
            unitConfig.DefaultDependencies = "no";

            serviceConfig = {
              Type = "oneshot";
              ExecStart = [
                "${installSecretTarball}/bin/install-secret-tarball ${config.clan.core.vars.password-store.secretLocation}/secrets_for_users.tar.gz /run/user-secrets"
              ];
              RemainAfterExit = true;
            };
          };
          pass-install-secrets = lib.mkIf normalSecrets {
            wantedBy = [ "sysinit.target" ];
            after = [ "systemd-sysusers.service" ];
            unitConfig.DefaultDependencies = "no";

            serviceConfig = {
              Type = "oneshot";
              ExecStart = [
                "${installSecretTarball}/bin/install-secret-tarball ${config.clan.core.vars.password-store.secretLocation}/secrets.tar.gz /run/secrets"
              ];
              RemainAfterExit = true;
            };
          };
        };
  };

}
