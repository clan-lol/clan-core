{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/user";
  manifest.description = ''
    An instance of this module will create a user account on the added machines,
    along with a generated password that is constant across machines and user settings.
  '';
  manifest.categories = [ "System" ];
  manifest.readme = builtins.readFile ./README.md;

  roles.default = {
    interface =
      { lib, ... }:
      {
        options = {
          user = lib.mkOption {
            type = lib.types.str;
            example = "alice";
            description = "The user the password should be generated for.";
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
        };
      };

    perInstance =
      { settings, ... }:
      {
        nixosModule =
          {
            config,
            pkgs,
            lib,
            ...
          }:
          {
            users.users.${settings.user} = {
              isNormalUser = if settings.user == "root" then false else true;
              extraGroups = settings.groups;

              hashedPasswordFile =
                config.clan.core.vars.generators."user-password-${settings.user}".files.user-password-hash.path;
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

              script =
                (
                  if settings.prompt then
                    ''
                      prompt_value=$(cat "$prompts"/user-password)
                      if [[ -n "''${prompt_value-}" ]]; then
                        echo "$prompt_value" | tr -d "\n" > "$out"/user-password
                      else
                        xkcdpass --numwords 4 --delimiter - --count 1 | tr -d "\n" > "$out"/user-password
                      fi
                    ''
                  else
                    ''
                      xkcdpass --numwords 4 --delimiter - --count 1 | tr -d "\n" > "$out"/user-password
                    ''
                )
                + ''
                  mkpasswd -s -m sha-512 < "$out"/user-password | tr -d "\n" > "$out"/user-password-hash
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
