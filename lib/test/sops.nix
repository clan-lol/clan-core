# nixosModule
{ config, lib, ... }:
let
  testAgeKey = lib.strings.trim (builtins.readFile ../../checks/assets/test-age-key.txt);
in
{
  # configures a static age-key to skip the age-key generation
  sops.age.keyFile = "/run/age-key.txt";
  system.activationScripts =
    let
      # https://github.com/Mic92/sops-nix/blob/61154300d945f0b147b30d24ddcafa159148026a/modules/sops/default.nix#L27
      hasRegularSecrets = lib.filterAttrs (_: v: !v.neededForUsers) config.sops.secrets != { };
      hasUserSecrets = lib.filterAttrs (_: v: v.neededForUsers) config.sops.secrets != { };
    in
    {
      age-key.text = ''
        echo ${testAgeKey} > /run/age-key.txt
      '';
    }
    // lib.optionalAttrs hasRegularSecrets {
      setupSecrets.deps = [ "age-key" ];
    }
    // lib.optionalAttrs hasUserSecrets {
      setupSecretsForUsers.deps = [ "age-key" ];
    };
}
