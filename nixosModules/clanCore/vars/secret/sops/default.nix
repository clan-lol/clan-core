{
  _class,
  config,
  lib,
  pkgs,
  ...
}:
let

  mapGeneratorsToSopsSecrets = import ./generators-to-sops.nix { inherit lib; };

  machineName = config.clan.core.settings.machine.name;
in
{
  options.clan.core.vars.sops = {
    secretUploadDirectory = lib.mkOption {
      type = lib.types.path;
      default = "/var/lib/sops-nix";
      description = ''
        The directory where sops-related files are uploaded to on the target machine.
        This includes the age private key used for decryption and activation secrets.
      '';
    };
  };

  config.clan.core.vars.settings = lib.mkIf (config.clan.core.vars.settings.secretStore == "sops") {
    # Before we generate a secret we cannot know the path yet, so we need to set it to an empty string
    fileModule = file: {
      path = lib.mkIf file.config.secret (
        if file.config.neededFor == "partitioning" then
          "/run/partitioning-secrets/${file.config.generatorName}/${file.config.name}"
        else if file.config.neededFor == "activation" then
          "${config.clan.core.vars.sops.secretUploadDirectory}/activation/${file.config.generatorName}/${file.config.name}"
        else
          config.sops.secrets.${"vars/${file.config.generatorName}/${file.config.name}"}.path
            or "/no-such-path"
      );
    };
    secretModule = "clan_cli.vars.secret_modules.sops";
  };

  config.sops = lib.mkIf (config.clan.core.vars.settings.secretStore == "sops") {
    #
    secrets = mapGeneratorsToSopsSecrets {
      inherit machineName;
      directory = config.clan.core.settings.directory;
      class = _class;
      generators = config.clan.core.vars.generators;
    };

    # To get proper error messages about missing secrets we need a dummy secret file that is always present
    defaultSopsFile = lib.mkIf config.sops.validateSopsFiles (
      lib.mkDefault (builtins.toString (pkgs.writeText "dummy.yaml" ""))
    );
    age.keyFile = lib.mkIf (builtins.pathExists (
      config.clan.core.settings.directory + "/sops/secrets/${machineName}-age.key/secret"
    )) (lib.mkDefault "${config.clan.core.vars.sops.secretUploadDirectory}/key.txt");
  };
}
