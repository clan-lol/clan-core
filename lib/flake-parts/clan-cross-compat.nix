# Cross-platform compatibility checks for clanTests.
#
# Evaluates each test with a cross-compilation nixpkgs instance
# (x86_64-linux -> aarch64-linux) and verifies that all transitive
# .drv dependencies use the expected build platform.
# This catches packages pinned to a specific platform via flake outputs
# instead of using pkgs.callPackage.
#
# Only runs on x86_64-linux.
{
  lib,
  self,
  nixosLib,
  crossPkgs,
}:
let
  mkCheck =
    pkgs: name: testModule:
    let
      crossTest = nixosLib.runTest (
        { ... }:
        {
          imports = [
            self.modules.nixosTest.clanTest
            testModule
          ];

          hostPkgs = pkgs;

          defaults = {
            imports = [
              { _module.args.clan-core = self; }
            ];
            nixpkgs.pkgs = crossPkgs;
          };
        }
      );
    in
    pkgs.runCommand "check-cross-compat-${name}"
      {
        nativeBuildInputs = [ pkgs.python3 ];
        drvPath = builtins.unsafeDiscardOutputDependency crossTest.config.driver.drvPath;
        moduleName = name;
      }
      ''
        python3 ${../clanTest/check-cross-compat.py} "$moduleName" "$drvPath" "x86_64-linux"
        touch $out
      '';

  mkAllChecks =
    pkgs: tests: testModules:
    let
      crossCompatChecks = lib.filterAttrs (_: v: v != null) (
        lib.mapAttrs (
          name: test:
          if test.config.clan.test.skipCrossCheck then null else mkCheck pkgs name testModules.${name}
        ) tests
      );
    in
    pkgs.runCommand "clan-cross-compat"
      {
        passthru = { inherit crossCompatChecks; };
      }
      (
        lib.concatStringsSep "\n" (
          lib.mapAttrsToList (_: drv: "echo '${drv}' > /dev/null") crossCompatChecks
        )
        + "\ntouch $out\n"
      );
in
{
  inherit mkCheck mkAllChecks;
}
