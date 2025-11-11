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
    genAttrs
    hasPrefix
    pathExists
    ;
  nixosLib = import (self.inputs.nixpkgs + "/nixos/lib") { };
in
{
  imports = filter pathExists [
    ./devshell/flake-module.nix
    ./flash/flake-module.nix
    ./installation/flake-module.nix
    ./update/flake-module.nix
    ./morph/flake-module.nix
    ./nixos-documentation/flake-module.nix
    ./dont-depend-on-repo-root.nix
    # clan core submodule tests
    ../nixosModules/clanCore/machine-id/tests/flake-module.nix
    ../nixosModules/clanCore/postgresql/tests/flake-module.nix
    ../nixosModules/clanCore/state-version/tests/flake-module.nix
  ];
  flake.check = genAttrs [ "x86_64-linux" "aarch64-darwin" ] (
    system:
    let
      checks = filterAttrs (
        name: _check:
        !(hasPrefix "nixos-test-" name)
        && !(hasPrefix "nixos-" name)
        && !(hasPrefix "darwin-test-" name)
        && !(hasPrefix "service-" name)
        && !(hasPrefix "vars-check-" name)
        && !(hasPrefix "devShell-" name)
        && !(elem name [
          "clan-deps"
        ])
      ) self.checks.${system};
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
            # reference to nixpkgs for the current system with patched systemd
            pkgs = pkgs.extend (
              _final: _prev: {
                systemd = self'.packages.systemd;
              }
            );
            inherit lib nixosLib;
            # this gives us a reference to our flake but also all flake inputs
            inherit self;
            inherit (self) clanLib;
            clan-core = self;
          };
          nixosTests =
            lib.optionalAttrs (pkgs.stdenv.isLinux) {

              # Base Tests
              nixos-test-secrets = self.clanLib.test.baseTest ./secrets nixosTestArgs;
              nixos-test-wayland-proxy-virtwl = self.clanLib.test.baseTest ./wayland-proxy-virtwl nixosTestArgs;

              # Container Tests
              nixos-test-container = self.clanLib.test.containerTest ./container nixosTestArgs;
              nixos-systemd-abstraction = self.clanLib.test.containerTest ./systemd-abstraction nixosTestArgs;
              nixos-test-user-firewall-iptables = self.clanLib.test.containerTest ./user-firewall/iptables.nix nixosTestArgs;
              nixos-test-user-firewall-nftables = self.clanLib.test.containerTest ./user-firewall/nftables.nix nixosTestArgs;
              nixos-test-extra-python-packages = self.clanLib.test.containerTest ./test-extra-python-packages nixosTestArgs;

              service-dummy-test = import ./service-dummy-test nixosTestArgs;
              service-dummy-test-from-flake = import ./service-dummy-test-from-flake nixosTestArgs;
            }
            # LLM test is too slow on aarch64 (inference times exceed timeout)
            // lib.optionalAttrs (pkgs.stdenv.isLinux && !pkgs.stdenv.isAarch64) {
              nixos-llm-test = self.clanLib.test.containerTest ./llm nixosTestArgs;
            };

          packagesToBuild = lib.removeAttrs self'.packages [
            # exclude the check that checks that nothing depends on the repo root
            # We might want to include this later once everything is fixed
            "dont-depend-on-repo-root"
          ];

          # Temporary workaround: Filter out docs package and devshell for aarch64-darwin due to CI builder hangs
          # TODO: Remove this filter once macOS CI builder is updated
          flakeOutputs =
            lib.mapAttrs' (
              name: config: lib.nameValuePair "nixos-${name}" config.config.system.build.toplevel
            ) (lib.filterAttrs (n: _: !lib.hasPrefix "test-" n) self.nixosConfigurations)
            // lib.mapAttrs' (
              name: config: lib.nameValuePair "darwin-${name}" config.config.system.build.toplevel
            ) (self.darwinConfigurations or { })
            // lib.mapAttrs' (n: lib.nameValuePair "package-${n}") (
              if system == "aarch64-darwin" then
                lib.filterAttrs (n: _: n != "docs" && n != "deploy-docs" && n != "option-search") packagesToBuild
              else
                packagesToBuild
            )
            // lib.mapAttrs' (n: lib.nameValuePair "devShell-${n}") (
              if system == "aarch64-darwin" then
                lib.filterAttrs (n: _: n != "docs") self'.devShells
              else
                self'.devShells
            )
            // lib.mapAttrs' (name: config: lib.nameValuePair "home-manager-${name}" config.activation-script) (
              self'.legacyPackages.homeConfigurations or { }
            );
        in
        nixosTests // flakeOutputs;
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
