{
  pkgs,
  nixosLib,
  clan-core,
  ...
}:

nixosLib.runTest (
  { hostPkgs, config, ... }:
  {
    imports = [
      clan-core.modules.nixosTest.clanTest
    ];

    hostPkgs = pkgs;

    # This tests the compatibility of the inventory
    # With the test framework
    # - clan.service modules
    name = "service-dummy-test-from-flake";

    clan.test.fromFlake = ./.;

    extraPythonPackages = _p: [
      clan-core.legacyPackages.${hostPkgs.system}.nixosTestLib
    ];

    testScript =
      { nodes, ... }:
      ''
        import subprocess
        import tempfile
        from nixos_test_lib.nix_setup import setup_nix_in_nix

        with tempfile.TemporaryDirectory() as temp_dir:
          setup_nix_in_nix(temp_dir, None)  # No closure info for this test

          start_all()
          admin1.wait_for_unit("multi-user.target")
          peer1.wait_for_unit("multi-user.target")

          # peer1 should have the 'hello' file
          peer1.succeed("cat ${nodes.peer1.clan.core.vars.generators.new-service.files.not-a-secret.path}")

          ls_out = peer1.succeed("ls -la ${nodes.peer1.clan.core.vars.generators.new-service.files.a-secret.path}")
          # Check that the file is owned by 'nobody'
          assert "nobody" in ls_out, f"File is not owned by 'nobody': {ls_out}"
          # Check that the file is in the 'users' group
          assert "users" in ls_out, f"File is not in the 'users' group: {ls_out}"
          # Check that the file is in the '0644' mode
          assert "-rw-r--r--" in ls_out, f"File is not in the '0644' mode: {ls_out}"

          # Run clan command
          result = subprocess.run(
              ["${
                clan-core.packages.${hostPkgs.system}.clan-cli
              }/bin/clan", "machines", "list", "--flake", "${config.clan.test.flakeForSandbox}"],
              check=True
          )
      '';
  }
)
