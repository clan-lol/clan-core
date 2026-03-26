# nixosModule — test helper for the age secret backend.
# Replaces sopsModule in test defaults: provisions a static age machine key
# so that age.nix activation scripts can decrypt secrets at boot.
{ config, lib, ... }:
let
  testAgeKey = lib.strings.trim (
    builtins.readFile ../../nixosModules/clanCore/vars/tests/age-fixtures/key.txt
  );

  hasSecrets = phase: lib.any (
    gen: lib.any (file: file.secret && file.deploy && file.neededFor == phase) (lib.attrValues gen.files)
  ) (lib.attrValues config.clan.core.vars.generators);
in
{
  clan.core.vars.settings.secretStore = "age";
  clan.core.vars.enableConsistencyCheck = false;

  system.activationScripts.testAgeKeySetup = {
    text = ''
      mkdir -p /etc/secret-vars
      cat > /etc/secret-vars/key.txt << 'AGEKEY'
      ${testAgeKey}
      AGEKEY
      chmod 600 /etc/secret-vars/key.txt
    '';
    deps = [ "specialfs" ];
  };

  # Wire age decryption scripts to run after key setup
  system.activationScripts.setupSecrets = lib.mkIf (hasSecrets "services") {
    deps = [ "testAgeKeySetup" ];
  };
  system.activationScripts.setupUserSecrets = lib.mkIf (hasSecrets "users") {
    deps = [ "testAgeKeySetup" ];
  };
}
