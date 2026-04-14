{ lib, ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/user";
  manifest.description = ''
    An instance of this module will create a user account on the added machines,
    along with a generated password that is constant across machines and user settings.
    Optionally exports identity metadata (email, groups) via the `auth` export type
    for consumption by IdP clan services (Authelia, Kanidm, etc.).
  '';
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;
  manifest.exports.out = [ "auth" ];

  roles.default = {
    description = "Placeholder role to apply the user service";
    interface =
      { lib, ... }:
      {
        options = {
          user = lib.mkOption {
            type = lib.types.str;
            defaultText = "$'{instanceName}";
            example = "alice";
            description = "The username for this account.";
          };
          systemUser = lib.mkOption {
            type = lib.types.bool;
            default = true;
            description = ''
              Whether to create a Unix system account for this user.

              Set to `false` for identity-only users who should exist in the
              IdP (Authelia, Kanidm, etc.) but have no shell access on any
              machine. The `auth.user` identity export still flows when
              `identity.email` is set, regardless of this flag.
            '';
          };
          prompt = lib.mkOption {
            type = lib.types.bool;
            default = true;
            example = false;
            description = ''
              Whether the user should be prompted for a password.

              Effects:

              - *enabled* (`true`) - Prompt for a password during the machine installation or update workflow.
              - *disabled* (`false`) - Generate a password during the machine installation or update workflow.

              The password can be shown in two steps:

              - `clan vars list <machine-name>`
              - `clan vars get <machine-name> <name-of-password-variable>`
            '';
          };
          groups = lib.mkOption {
            type = lib.types.listOf lib.types.str;
            default = [ ];
            example = [
              "wheel"
              "networkmanager"
              "video"
              "input"
            ];
            description = ''
              Additional groups the user should be added to.
              You can add any group that exists on your system.
              Make sure these group exists on all machines where the user is enabled.

              Commonly used groups:

              - "wheel" - Allows the user to run commands as root using `sudo`.
              - "networkmanager" - Allows the user to manage network connections.
              - "video" - Allows the user to access video devices.
              - "input" - Allows the user to access input devices.
            '';
          };
          share = lib.mkOption {
            type = lib.types.bool;
            default = false;
            example = true;
            description = ''
              Weather the user should have the same password on all machines.

              By default, you will be prompted for a new password for every host.
              Unless `generate` is set to `true`.
            '';
          };

          identity = lib.mkOption {
            type = lib.types.attrsOf (
              lib.types.submodule {
                options = {
                  email = lib.mkOption {
                    type = lib.types.str;
                    default = "";
                    example = "alice@example.com";
                    description = ''
                      Email for this IdP account. Defaults to <user>@mail.<meta.domain>.
                    '';
                  };
                  groups = lib.mkOption {
                    type = lib.types.listOf lib.types.str;
                    default = [ ];
                    example = [
                      "admins"
                      "users"
                    ];
                    description = ''
                      IdP-level groups. Control OIDC client access policies
                      (e.g. "miniflux-users" gates miniflux access).
                    '';
                  };
                  displayname = lib.mkOption {
                    type = lib.types.nullOr lib.types.str;
                    default = null;
                    description = "Display name. Defaults to the username.";
                  };
                };
              }
            );
            default = { };
            description = ''
              IdP identities keyed by IdP instance name. Each entry creates
              a user account in the corresponding IdP clan service. Example:
              identity.main = { groups = [ "users" ]; } creates an account
              in the IdP instance named "main" in inventory.
            '';
            example = lib.literalExpression ''
              {
                main = {
                  email = "alice@example.com";
                  groups = [ "admins" "users" ];
                };
              }
            '';
          };

          openssh.authorizedKeys = {
            keys = lib.mkOption {
              type = lib.types.listOf lib.types.singleLineStr;
              default = [ ];
              description = ''
                A list of verbatim OpenSSH public keys that should be added to the
                user's authorized keys. The keys are added to a file that the SSH
                daemon reads in addition to the the user's authorized_keys file.
              '';
              example = [
                "ssh-rsa AAAAB3NzaC1yc2etc/etc/etcjwrsh8e596z6J0l7 example@host"
                "ssh-ed25519 AAAAC3NzaCetcetera/etceteraJZMfk3QPfQ foo@bar"
              ];
            };

            keyFiles = lib.mkOption {
              type = lib.types.listOf lib.types.path;
              default = [ ];
              description = ''
                A list of files each containing one OpenSSH public key that should be
                added to the user's authorized keys. The contents of the files are
                read at build time and added to a file that the SSH daemon reads in
                addition to the the user's authorized_keys file. You can combine the
                `keyFiles` and `keys` options.
              '';
            };
          };
        };
      };

    perInstance =
      {
        settings,
        extendSettings,
        instanceName,
        mkExports,
        meta,
        ...
      }:
      {
        exports = mkExports (
          lib.optionalAttrs (settings.identity != { }) {
            # Keyed by IdP instance name — each entry becomes a user in that IdP
            auth.users = lib.mapAttrs (_idpName: id: {
              username = settings.user;
              email = if id.email != "" then id.email else "${settings.user}@mail.${meta.domain}";
              groups = id.groups;
              displayname = if id.displayname != null then id.displayname else settings.user;
            }) settings.identity;
          }
        );

        nixosModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          let
            settings = extendSettings { user = lib.mkOptionDefault instanceName; };
          in
          lib.mkIf settings.systemUser {
            users.users.${settings.user} = {
              isNormalUser = if settings.user == "root" then false else true;
              extraGroups = settings.groups;

              hashedPasswordFile =
                config.clan.core.vars.generators."user-password-${settings.user}".files.user-password-hash.path;
              openssh.authorizedKeys = settings.openssh.authorizedKeys;
            };

            clan.core.vars.generators."user-password-${settings.user}" = {
              files.user-password-hash.neededFor = "users";
              files.user-password-hash.restartUnits = lib.optional (config.services.userborn.enable) "userborn.service";
              files.user-password.deploy = false;

              prompts.user-password = lib.mkIf settings.prompt {
                display = {
                  group = settings.user;
                  label = "password";
                  required = false;
                  helperText = ''
                    Your password will be encrypted and stored securely using the secret store you've configured.
                  '';
                };
                type = "hidden";
                persist = true;
                description = "Leave empty to generate automatically";
              };

              runtimeInputs = [
                pkgs.coreutils
                pkgs.xkcdpass
                pkgs.mkpasswd
              ];

              share = settings.share;

              script =
                (
                  if settings.prompt then
                    ''
                      prompt_value=$(cat "$prompts"/user-password)
                      if [[ -n "''${prompt_value-}" ]]; then
                        echo "$prompt_value" | tr -d "\n" > "$out"/user-password
                      else
                        xkcdpass --numwords 6 --delimiter - --count 1 | tr -d "\n" > "$out"/user-password
                      fi
                    ''
                  else
                    ''
                      xkcdpass --numwords 6 --delimiter - --count 1 | tr -d "\n" > "$out"/user-password
                    ''
                )
                + ''
                  mkpasswd -s < "$out"/user-password | tr -d "\n" > "$out"/user-password-hash
                '';
            };
          };
      };
  };

  perMachine = {
    nixosModule = {
      # Immutable users to ensure that this module has exclusive control over the users.
      users.mutableUsers = false;
    };
  };
}
