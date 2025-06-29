{ self, lib, ... }:
let
  inherit (lib)
    filter
    pathExists
    ;
  nixosLib = import (self.inputs.nixpkgs + "/nixos/lib") { };
in
{
  imports = filter pathExists [
    ./backups/flake-module.nix
    ../nixosModules/clanCore/machine-id/tests/flake-module.nix
    ./devshell/flake-module.nix
    ./flash/flake-module.nix
    ./impure/flake-module.nix
    ./installation/flake-module.nix
    ./morph/flake-module.nix
    ./nixos-documentation/flake-module.nix
    ./dont-depend-on-repo-root.nix
  ];
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
            secrets = self.clanLib.test.baseTest ./secrets nixosTestArgs;
            borgbackup-legacy = self.clanLib.test.baseTest ./borgbackup-legacy nixosTestArgs;
            wayland-proxy-virtwl = self.clanLib.test.baseTest ./wayland-proxy-virtwl nixosTestArgs;

            # Container Tests
            container = self.clanLib.test.containerTest ./container nixosTestArgs;
            zt-tcp-relay = self.clanLib.test.containerTest ./zt-tcp-relay nixosTestArgs;
            matrix-synapse = self.clanLib.test.containerTest ./matrix-synapse nixosTestArgs;
            postgresql = self.clanLib.test.containerTest ./postgresql nixosTestArgs;
            user-firewall-iptables = self.clanLib.test.containerTest ./user-firewall/iptables.nix nixosTestArgs;
            user-firewall-nftables = self.clanLib.test.containerTest ./user-firewall/nftables.nix nixosTestArgs;

            dummy-inventory-test = import ./dummy-inventory-test nixosTestArgs;
            dummy-inventory-test-from-flake = import ./dummy-inventory-test-from-flake nixosTestArgs;
            data-mesher = import ./data-mesher nixosTestArgs;
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
            chmod +w $out/flake.lock
            cp ${../flake.lock} $out/flake.lock
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
            secrets = import ./secrets nixosTestArgs;
            container = import ./container nixosTestArgs;
            # Clan app tests
            app-ocr = self.clanLib.test.baseTest ./app-ocr nixosTestArgs;
          };
      };
    };
}
