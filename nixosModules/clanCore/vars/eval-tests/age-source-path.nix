# Pins the on-disk layout for age-encrypted vars secrets.
#
# Why this test exists:
#   The Nix age backend (../secret/age.nix) and the Python age backend
#   (clan_lib/vars/secret_modules/age.py:secret_path) must agree on where
#   encrypted secrets live on disk. A divergence is silent: the Nix side
#   skips secrets whose `pathExists` returns false, the activation script
#   becomes empty, and consumers like users.users.<u>.hashedPasswordFile
#   fail at boot with "password file does not exist".
#
#   This test asserts that ../secret/age-source-path.nix produces paths
#   that match the on-disk fixtures under ../tests/secrets/clan-vars,
#   which are written using the same layout as the Python writer.
#
#   Update fixtures and Python writer together; this test then enforces
#   the Nix side stays aligned.
{ ... }:
let
  encryptedSourcePath = import ../secret/age-source-path.nix;

  fixturesRoot = ../tests;

  # The fixtures committed under nixosModules/clanCore/vars/tests/secrets
  # were produced by the Python writer. Each entry must resolve to a real
  # file via encryptedSourcePath; if any layout change drops a path
  # segment, the assertion below trips.
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
  # Every fixture must be reachable through encryptedSourcePath. If any
  # entry returns false, either the fixture moved or the helper dropped
  # a segment — both are layout-breaking changes and require a matching
  # Python update.
  test_all_fixtures_reachable = {
    expr = map (r: builtins.pathExists r.path) resolved;
    expected = builtins.genList (_: true) (builtins.length fixtures);
  };

  # Pin the literal path shape for a representative per-machine secret.
  # Catches accidental refactors that compute a different string even
  # when the fixture happens to also exist at the new location.
  test_per_machine_layout = {
    expr = encryptedSourcePath "/clan" "per-machine/jon/zerotier" "identity";
    expected = "/clan/secrets/clan-vars/per-machine/jon/zerotier/identity/identity.age";
  };

  # Pin the literal shape for shared and per-export scopes too — these
  # placement classes flow through the same helper.
  test_shared_layout = {
    expr = encryptedSourcePath "/clan" "shared/wifi" "psk";
    expected = "/clan/secrets/clan-vars/shared/wifi/psk/psk.age";
  };

  test_per_export_layout = {
    expr = encryptedSourcePath "/clan" "per-export/A/one" "foo";
    expected = "/clan/secrets/clan-vars/per-export/A/one/foo/foo.age";
  };
}
