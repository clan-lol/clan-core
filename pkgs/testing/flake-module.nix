{
  perSystem = {
    legacyPackages.setupNixInNix = ''
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
        xargs cp --recursive --target "$CLAN_TEST_STORE/nix/store"  < "$closureInfo/store-paths"
        nix-store --load-db --store "$CLAN_TEST_STORE" < "$closureInfo/registration"
      fi
    '';
  };
}
