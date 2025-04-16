# nixosModule
{ config, lib, ... }:
{
  # configures a static age-key to skip the age-key generation
  sops.age.keyFile = "/run/age-key.txt";
  system.activationScripts =
    {
      setupSecrets.deps = [ "age-key" ];
      age-key.text = ''
        echo AGE-SECRET-KEY-1PL0M9CWRCG3PZ9DXRTTLMCVD57U6JDFE8K7DNVQ35F4JENZ6G3MQ0RQLRV > /run/age-key.txt
      '';
    }
    // lib.optionalAttrs (lib.filterAttrs (_: v: v.neededForUsers) config.sops.secrets != { }) {
      setupSecretsForUsers.deps = [ "age-key" ];
    };
}
