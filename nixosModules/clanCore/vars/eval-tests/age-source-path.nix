{ lib }:
let
  encryptedSourcePath = import ../secret/age-source-path.nix;
  encryptedRuntimePath = import ../secret/age-runtime-path.nix;
  encryptedStorePath = import ../secret/age-store-path.nix { inherit lib; };

  fixturesRoot = ../tests;

  # Two clan directories in the string form that `clan.directory` gets from
  # the flake. Both hold the same .age file. Only the first one holds the
  # other fixtures.
  fullClanDir = "${fixturesRoot}";
  secretOnlyClanDir = "${lib.fileset.toSource {
    root = fixturesRoot;
    fileset = fixturesRoot + "/secrets/clan-vars/shared/shared-generator/shared-secret";
  }}";
  storePath = clanDir: encryptedStorePath clanDir "shared/shared-generator" "shared-secret";

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

  # The store path must depend on the .age file only. A path below the clan
  # directory changes with each unrelated file in it.
  test_store_path_ignores_other_files = {
    expr = storePath fullClanDir == storePath secretOnlyClanDir;
    expected = true;
  };

  # The string is a store path of its own, not a path below the clan directory.
  # An attribute name cannot carry string context, so the key drops it.
  test_store_path_is_own_context = {
    expr = builtins.getContext (storePath fullClanDir);
    expected = {
      ${builtins.unsafeDiscardStringContext (storePath fullClanDir)} = {
        path = true;
      };
    };
  };

  test_store_path_missing_file = {
    expr = encryptedStorePath fullClanDir "shared/shared-generator" "no-such-secret";
    expected = null;
  };

  # External store: the runtime path must mirror the upload layout of
  # populate_dir in age.py (vars/{rel_dir}/{name}/{name}.age).
  test_external_runtime_layout = {
    expr = encryptedRuntimePath "/etc/secret-vars" "per-machine/jon/zerotier" "identity";
    expected = "/etc/secret-vars/vars/per-machine/jon/zerotier/identity/identity.age";
  };
}
