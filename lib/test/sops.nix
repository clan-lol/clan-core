# nixosModule
{ config, lib, ... }:
{
  # configures a static age-key to skip the age-key generation
  sops.age.keyFile = "/run/age-key.txt";
  system.activationScripts =
    let
      # https://github.com/Mic92/sops-nix/blob/61154300d945f0b147b30d24ddcafa159148026a/modules/sops/default.nix#L27
      hasRegularSecrets = lib.filterAttrs (_: v: v.neededForUsers) config.sops.secrets != { };
    in
    {
      age-key.text = ''
        echo AGE-SECRET-KEY-1PL0M9CWRCG3PZ9DXRTTLMCVD57U6JDFE8K7DNVQ35F4JENZ6G3MQ0RQLRV > /run/age-key.txt
      '';
    }
    // lib.optionalAttrs (hasRegularSecrets) {
      setupSecrets.deps = [ "age-key" ];
      setupSecretsForUsers.deps = [ "age-key" ];
    };
}
