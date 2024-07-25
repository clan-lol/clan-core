{
  config,
  lib,
  pkgs,
  ...
}:
let

  inherit (lib) flip;

  inherit (import ./funcs.nix { inherit lib; }) listVars;

  varsDir = config.clan.core.clanDir + "/sops/vars";

  vars = listVars varsDir;

in
{
  config.clan.core.vars.settings = lib.mkIf (config.clan.core.vars.settings.secretStore == "sops") {
    # Before we generate a secret we cannot know the path yet, so we need to set it to an empty string
    fileModule = file: {
      path = lib.mkIf file.config.secret (
        config.sops.secrets.${"vars-${config.clan.core.machineName}-${file.config.generatorName}-${file.config.name}"}.path
          or "/no-such-path"
      );
    };
    secretModule = "clan_cli.vars.secret_modules.sops";
    secretUploadDirectory = lib.mkDefault "/var/lib/sops-nix";
  };

  config.sops = lib.mkIf (config.clan.core.vars.settings.secretStore == "sops") {
    secrets = lib.listToAttrs (
      flip map vars (secret: {
        name = secret.name;
        value = {
          sopsFile =
            config.clan.core.clanDir + "/sops/vars/${secret.machine}/${secret.generator}/${secret.name}/secret";
          format = "binary";
        };
      })
    );
    # To get proper error messages about missing secrets we need a dummy secret file that is always present
    defaultSopsFile = lib.mkIf config.sops.validateSopsFiles (
      lib.mkDefault (builtins.toString (pkgs.writeText "dummy.yaml" ""))
    );
    age.keyFile = lib.mkIf (builtins.pathExists (
      config.clan.core.clanDir + "/sops/secrets/${config.clan.core.machineName}-age.key/secret"
    )) (lib.mkDefault "/var/lib/sops-nix/key.txt");
  };
}
