{
  self,
  lib,
  inputs,
  ...
}:
let
  inherit (lib)
    attrNames
    attrValues
    elem
    filter
    filterAttrs
    flip
    genAttrs
    hasPrefix
    pathExists
    ;
  nixosLib = import (self.inputs.nixpkgs + "/nixos/lib") { };
in
{
  imports =
    let
      clanCoreModulesDir = ../nixosModules/clanCore;
      getClanCoreTestModules =
        let
          moduleNames = attrNames (builtins.readDir clanCoreModulesDir);
          testPaths = map (
            moduleName: clanCoreModulesDir + "/${moduleName}/tests/flake-module.nix"
          ) moduleNames;
        in
        filter pathExists testPaths;
    in
    getClanCoreTestModules
    ++ filter pathExists [
      ./devshell/flake-module.nix
      ./flash/flake-module.nix
      ./impure/flake-module.nix
      ./installation/flake-module.nix
      ./update/flake-module.nix
      ./morph/flake-module.nix
      ./nixos-documentation/flake-module.nix
      ./dont-depend-on-repo-root.nix
    ];
  flake.check = genAttrs [ "x86_64-linux" "aarch64-darwin" ] (
    system:
    let
      checks = flip filterAttrs self.checks.${system} (
        name: _check:
        !(hasPrefix "nixos-test-" name)
        && !(hasPrefix "nixos-" name)
        && !(hasPrefix "darwin-test-" name)
        && !(hasPrefix "service-" name)
        && !(hasPrefix "vars-check-" name)
        && !(hasPrefix "devShell-" name)
        && !(elem name [
          "clan-core-for-checks"
          "clan-deps"
        ])
      );
    in
    inputs.nixpkgs.legacyPackages.${system}.runCommand "fast-flake-checks-${system}"
      { passthru.checks = checks; }
      ''
        echo "Executed the following checks for ${system}..."
        echo "  - ${lib.concatStringsSep "\n" (map (n: "  - " + n) (attrNames checks))}"
        echo ${toString (attrValues checks)} >/dev/null
        echo "All checks succeeded"
        touch $out
      ''
  );
  perSystem =
    {
      pkgs,
      lib,
      self',
      system,
      ...
    }:
    {
      checks =
        let
          nixosTestArgs = {
            # reference to nixpkgs for the current system
            inherit pkgs lib nixosLib;
            # this gives us a reference to our flake but also all flake inputs
            inherit self;
            inherit (self) clanLib;
            clan-core = self;
          };
          nixosTests = lib.optionalAttrs (pkgs.stdenv.isLinux) {

            # Base Tests
            nixos-test-secrets = self.clanLib.test.baseTest ./secrets nixosTestArgs;
            nixos-test-borgbackup-legacy = self.clanLib.test.baseTest ./borgbackup-legacy nixosTestArgs;
            nixos-test-wayland-proxy-virtwl = self.clanLib.test.baseTest ./wayland-proxy-virtwl nixosTestArgs;

            # Container Tests
            nixos-test-container = self.clanLib.test.containerTest ./container nixosTestArgs;
            nixos-test-zt-tcp-relay = self.clanLib.test.containerTest ./zt-tcp-relay nixosTestArgs;
            nixos-test-user-firewall-iptables = self.clanLib.test.containerTest ./user-firewall/iptables.nix nixosTestArgs;
            nixos-test-user-firewall-nftables = self.clanLib.test.containerTest ./user-firewall/nftables.nix nixosTestArgs;

            service-dummy-test = import ./service-dummy-test nixosTestArgs;
            service-dummy-test-from-flake = import ./service-dummy-test-from-flake nixosTestArgs;
          };

          packagesToBuild = lib.removeAttrs self'.packages [
            # exclude the check that checks that nothing depends on the repo root
            # We might want to include this later once everything is fixed
            "dont-depend-on-repo-root"
          ];

          flakeOutputs =
            lib.mapAttrs' (
              name: config: lib.nameValuePair "nixos-${name}" config.config.system.build.toplevel
            ) (lib.filterAttrs (n: _: !lib.hasPrefix "test-" n) self.nixosConfigurations)
            // lib.mapAttrs' (
              name: config: lib.nameValuePair "darwin-${name}" config.config.system.build.toplevel
            ) (self.darwinConfigurations or { })
            // lib.mapAttrs' (n: lib.nameValuePair "package-${n}") packagesToBuild
            // lib.mapAttrs' (n: lib.nameValuePair "devShell-${n}") self'.devShells
            // lib.mapAttrs' (name: config: lib.nameValuePair "home-manager-${name}" config.activation-script) (
              self'.legacyPackages.homeConfigurations or { }
            );
        in
        nixosTests
        // flakeOutputs
        // {
          # TODO: Automatically provide this check to downstream users to check their modules
          clan-modules-json-compatible =
            let
              allSchemas = lib.mapAttrs (
                _n: m:
                let
                  schema =
                    (self.clanLib.evalService {
                      modules = [ m ];
                      prefix = [
                        "checks"
                        system
                      ];
                    }).config.result.api.schema;
                in
                schema
              ) self.clan.modules;
            in
            pkgs.runCommand "combined-result"
              {
                schemaFile = builtins.toFile "schemas.json" (builtins.toJSON allSchemas);
              }
              ''
                mkdir -p $out
                cat $schemaFile > $out/allSchemas.json
              '';

          clan-core-for-checks = pkgs.runCommand "clan-core-for-checks" { } ''
            cp -r ${pkgs.callPackage ./clan-core-for-checks.nix { }} $out
            chmod -R +w $out
            cp ${../flake.lock} $out/flake.lock

            # Create marker file to disable private flake loading in tests
            touch $out/.skip-private-inputs
          '';
        };
      packages = lib.optionalAttrs (pkgs.stdenv.isLinux) {
        run-vm-test-offline = pkgs.callPackage ../pkgs/run-vm-test-offline { };
      };
      legacyPackages = {
        nixosTests =
          let
            nixosTestArgs = {
              # reference to nixpkgs for the current system
              inherit pkgs;
              # this gives us a reference to our flake but also all flake inputs
              inherit self;
            };
          in
          lib.optionalAttrs (pkgs.stdenv.isLinux) {
            # import our test
            nixos-test-secrets = import ./secrets nixosTestArgs;
            nixos-test-container = import ./container nixosTestArgs;
            # Clan app tests
            nixos-test-app-ocr = self.clanLib.test.baseTest ./app-ocr nixosTestArgs;
          };
      };
    };
}
