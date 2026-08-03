# Pins the on-disk layout for age-encrypted vars secrets.
# ../secret/age.nix and age.py:secret_path must agree on it.
#
# Divergence is silent.
# age.nix skips secrets whose `pathExists` is false.
# The activation script becomes empty.
# Boot then fails on hashedPasswordFile: "password file does not exist".
#
# Fixtures live in ../tests/secrets/clan-vars and come from the Python writer.
# Change them and the writer together.
{ ... }:
let
  encryptedSourcePath = import ../secret/age-source-path.nix;

  fixturesRoot = ../tests;

  # Every fixture must resolve to a real file.
  # A dropped path segment trips the assertion below.
  fixtures = [
    {
      rel_dir = "shared/shared-generator";
      fileName = "shared-secret";
    }
    {
      rel_dir = "per-machine/machine/test-generator";
      fileName = "service-secret";
    }
    {
      rel_dir = "per-machine/machine/test-generator";
      fileName = "user-secret";
    }
    {
      rel_dir = "per-machine/machine/test-generator";
      fileName = "activation-secret";
    }
    {
      rel_dir = "per-machine/machine/perm-generator";
      fileName = "perm-secret";
    }
  ];

  resolved = map (f: {
    inherit (f) rel_dir fileName;
    path = encryptedSourcePath fixturesRoot f.rel_dir f.fileName;
  }) fixtures;
in
{
  # False means the fixture moved or the helper dropped a segment.
  # Both are layout breaks and need a matching Python change.
  test_all_fixtures_reachable = {
    expr = map (r: builtins.pathExists r.path) resolved;
    expected = builtins.genList (_: true) (builtins.length fixtures);
  };

  # Pin the literal string, not just reachability.
  # A refactor could compute a different path that also exists.
  test_per_machine_layout = {
    expr = encryptedSourcePath "/clan" "per-machine/jon/zerotier" "identity";
    expected = "/clan/secrets/clan-vars/per-machine/jon/zerotier/identity/identity.age";
  };

  # The other two placements use the same helper.
  test_shared_layout = {
    expr = encryptedSourcePath "/clan" "shared/wifi" "psk";
    expected = "/clan/secrets/clan-vars/shared/wifi/psk/psk.age";
  };

  test_per_export_layout = {
    expr = encryptedSourcePath "/clan" "per-export/A/one" "foo";
    expected = "/clan/secrets/clan-vars/per-export/A/one/foo/foo.age";
  };
}
