{
  perSystem =
    { pkgs, ... }:
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
            # ${pkgs.findutils}/bin/xargs ${pkgs.xcp}/bin/xcp --recursive --target-directory "$CLAN_TEST_STORE/nix/store"  < "$closureInfo/store-paths"
            ${pkgs.findutils}/bin/xargs ${pkgs.coreutils}/bin/cp --recursive --target "$CLAN_TEST_STORE/nix/store"  < "$closureInfo/store-paths"
            ${pkgs.nix}/bin/nix-store --load-db --store "$CLAN_TEST_STORE" < "$closureInfo/registration"
          fi
        '';

      };
    };
}
