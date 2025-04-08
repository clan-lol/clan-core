{
  pkgs,
  config,
  lib,
  ...
}:
let
  cfg = config.clan.user-password;
in
{
  options.clan.user-password = {
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

  config = {
    users.mutableUsers = false;
    users.users.${cfg.user} = {
      hashedPasswordFile = config.clan.core.vars.generators.user-password.files.user-password-hash.path;
      isNormalUser = lib.mkDefault true;
    };

    clan.core.vars.generators.user-password = {
      files.user-password-hash.neededFor = "users";

      prompts.user-password.type = "hidden";
      prompts.user-password.persist = true;
      prompts.user-password.description = "You can autogenerate a password, if you leave this prompt blank.";
      files.user-password.deploy = false;

      migrateFact = "user-password";
      runtimeInputs = [
        pkgs.coreutils
        pkgs.xkcdpass
        pkgs.mkpasswd
      ];
      script = ''
        prompt_value=$(cat $prompts/user-password)
        if [[ -n ''${prompt_value-} ]]; then
          echo $prompt_value | tr -d "\n" > $out/user-password
        else
          xkcdpass --numwords 3 --delimiter - --count 1 | tr -d "\n" > $out/user-password
        fi
        mkpasswd -s -m sha-512 < $out/user-password | tr -d "\n" > $out/user-password-hash
      '';
    };
  };
}
