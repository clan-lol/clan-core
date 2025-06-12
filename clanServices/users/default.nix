{ ... }:
{
  _class = "clan.service";
  manifest.name = "clan-core/users";
  manifest.description = "Automatically generates and configures a password for the specified user account.";
  manifest.categories = [ "System" ];

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
            description = "Whether the user should be prompted.";
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
            users.mutableUsers = false;
            users.users.${settings.user}.hashedPasswordFile =
              config.clan.core.vars.generators."user-password-${settings.user}".files.user-password-hash.path;

            clan.core.vars.generators."user-password-${settings.user}" = {

              # files.user-password-hash.neededFor = "users";
              files.user-password-hash.restartUnits = lib.optional (config.services.userborn.enable) "userborn.service";
              files.user-password.deploy = false;

              prompts.user-password = lib.mkIf settings.prompt {
                type = "hidden";
                persist = true;
                description = "You can autogenerate a password, if you leave this prompt blank.";
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
}
