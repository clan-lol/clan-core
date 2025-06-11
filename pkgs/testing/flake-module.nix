{
  perSystem = {
    legacyPackages = {
      setupNixInNix = ''
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
      setupNixInNixPython = ''
        from os import environ
        import subprocess
        from pathlib import Path
        environ['HOME'] = environ['TMPDIR']
        environ['NIX_STATE_DIR'] = environ['TMPDIR'] + '/nix'
        environ['NIX_CONF_DIR'] = environ['TMPDIR'] + '/etc'
        environ['IN_NIX_SANDBOX'] = '1'
        environ['CLAN_TEST_STORE'] = environ['TMPDIR'] + '/store'
        environ['LOCK_NIX'] = environ['TMPDIR'] + '/nix_lock'
        Path(environ['CLAN_TEST_STORE'] + '/nix/store').mkdir(parents=True, exist_ok=True)
        Path(environ['CLAN_TEST_STORE'] + '/nix/var/nix/gcroots').mkdir(parents=True, exist_ok=True)
        if 'closureInfo' in environ:
          subprocess.run(['cp', '--recursive', '--target', environ['CLAN_TEST_STORE'] + '/nix/store'] + environ['closureInfo'].split(), check=True)
          subprocess.run(['nix-store', '--load-db', '--store', environ['CLAN_TEST_STORE']] + ['<', environ['closureInfo'] + '/registration'], shell=True, check=True)
      '';
    };
  };
}
