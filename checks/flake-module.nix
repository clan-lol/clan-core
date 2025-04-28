{ self, lib, ... }:
let
  inherit (lib)
    filter
    pathExists
    ;
in
{
  imports = filter pathExists [
    ./backups/flake-module.nix
    ./devshell/flake-module.nix
    ./flash/flake-module.nix
    ./impure/flake-module.nix
    ./installation/flake-module.nix
    ./morph/flake-module.nix
    ./nixos-documentation/flake-module.nix
    ./sanity-checks/dont-depend-on-repo-root.nix
  ];
  perSystem =
    {
      pkgs,
      lib,
      self',
      ...
    }:
    {
      checks =
        let
          nixosTestArgs = {
            # reference to nixpkgs for the current system
            inherit pkgs lib;
            # this gives us a reference to our flake but also all flake inputs
            inherit self;
            inherit (self) clanLib;
          };
          nixosTests = lib.optionalAttrs (pkgs.stdenv.isLinux) {
            # Deltachat is currently marked as broken
            # deltachat = import ./deltachat nixosTestArgs;

            # Base Tests
            secrets = self.clanLib.test.baseTest ./secrets nixosTestArgs;
            borgbackup = self.clanLib.test.baseTest ./borgbackup nixosTestArgs;
            wayland-proxy-virtwl = self.clanLib.test.baseTest ./wayland-proxy-virtwl nixosTestArgs;

            # Container Tests
            container = self.clanLib.test.containerTest ./container nixosTestArgs;
            zt-tcp-relay = self.clanLib.test.containerTest ./zt-tcp-relay nixosTestArgs;
            matrix-synapse = self.clanLib.test.containerTest ./matrix-synapse nixosTestArgs;
            postgresql = self.clanLib.test.containerTest ./postgresql nixosTestArgs;

            # Clan Tests
            mumble = import ./mumble nixosTestArgs;
            dummy-inventory-test = import ./dummy-inventory-test nixosTestArgs;
            data-mesher = import ./data-mesher nixosTestArgs;
            syncthing = import ./syncthing nixosTestArgs;
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
                    (self.clanLib.inventory.evalClanService {
                      modules = [ m ];
                      key = "checks";
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
