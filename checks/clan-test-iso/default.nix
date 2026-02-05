{
  pkgs,
  nixosLib,
  clan-core,
  ...
}:
nixosLib.runTest (
  { hostPkgs, config, ... }:
  let
    closureInfo = pkgs.closureInfo {
      rootPaths = [
        pkgs.stdenv.drvPath
        config.clan.test.machinesCross.${pkgs.system}.peer1.config.system.build.images.iso.drvPath
        config.clan.test.systemsFile
      ];
    };
  in
  {
    imports = [
      clan-core.modules.nixosTest.clanTest
    ];

    hostPkgs = pkgs;

    # This tests the compatibility of the inventory
    # With the test framework
    # - clan.service modules
    name = "clan-test-iso";

    clan.test.fromFlake = ./.;

    extraPythonPackages = _p: [
      clan-core.legacyPackages.${hostPkgs.stdenv.hostPlatform.system}.nixosTestLib
    ];

    testScript =
      { ... }:
      ''
        import subprocess
        import tempfile
        from nixos_test_lib.nix_setup import setup_nix_in_nix

        with tempfile.TemporaryDirectory() as temp_dir:
          setup_nix_in_nix(temp_dir, "${closureInfo}")  # No closure info for this test

          start_all()

          result = subprocess.run(
              ["${
                clan-core.packages.${hostPkgs.stdenv.hostPlatform.system}.clan-cli
              }/bin/clan", "machines", "build", "peer1", "--format", "iso", "--flake", "${config.clan.test.flakeForSandbox}"],
              check=True
          )
      '';
  }
)
