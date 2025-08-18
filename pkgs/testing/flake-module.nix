{
  perSystem =
    { pkgs, lib, ... }:
    {
      legacyPackages = {
        setupNixInNix = ''
          set -xeu -o pipefail
          export HOME=$TMPDIR
          export NIX_STATE_DIR=$TMPDIR/nix
          export NIX_CONF_DIR=$TMPDIR/etc
          export IN_NIX_SANDBOX=1
          export CLAN_TEST_STORE=$TMPDIR/store
          # required to prevent concurrent 'nix flake lock' operations
          export LOCK_NIX=$TMPDIR/nix_lock
          mkdir -p "$CLAN_TEST_STORE/nix/store"
          mkdir -p "$CLAN_TEST_STORE/nix/var/nix/gcroots"
          if [[ -n "''${closureInfo-}" ]]; then
            ${pkgs.findutils}/bin/xargs ${pkgs.xcp}/bin/xcp --recursive --target-directory "$CLAN_TEST_STORE/nix/store"  < "$closureInfo/store-paths"
            ${pkgs.nix}/bin/nix-store --load-db --store "$CLAN_TEST_STORE" < "$closureInfo/registration"
          fi
        '';

        # NixOS test library combining port utils and clan VM test utilities
        nixosTestLib = pkgs.python3Packages.buildPythonPackage {
          pname = "nixos-test-lib";
          version = "1.0.0";
          format = "pyproject";
          src = lib.fileset.toSource {
            root = ./.;
            fileset = lib.fileset.unions [
              ./pyproject.toml
              ./nixos_test_lib
            ];
          };
          nativeBuildInputs = with pkgs.python3Packages; [
            setuptools
            wheel
          ];
          postPatch = ''
            substituteInPlace nixos_test_lib/nix_setup.py \
              --replace '@xcp@' '${pkgs.xcp}/bin/xcp' \
              --replace '@nix-store@' '${pkgs.nix}/bin/nix-store' \
              --replace '@xargs@' '${pkgs.findutils}/bin/xargs'
          '';
          doCheck = false;
        };

      };
    };
}
