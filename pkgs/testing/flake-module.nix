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

        setupNixInNixPythonPackage = pkgs.python3Packages.buildPythonPackage {
          pname = "setup-nix-in-nix";
          version = "1.0.0";
          format = "other";

          dontUnpack = true;

          installPhase = ''
            mkdir -p $out/${pkgs.python3.sitePackages}
            cat > $out/${pkgs.python3.sitePackages}/setup_nix_in_nix.py << 'EOF'
            from os import environ
            import subprocess
            from pathlib import Path

            def setup_nix_in_nix():
                """Set up a Nix store inside the test environment."""
                environ['HOME'] = environ['TMPDIR']
                environ['NIX_STATE_DIR'] = environ['TMPDIR'] + '/nix'
                environ['NIX_CONF_DIR'] = environ['TMPDIR'] + '/etc'
                environ['IN_NIX_SANDBOX'] = '1'
                environ['CLAN_TEST_STORE'] = environ['TMPDIR'] + '/store'
                environ['LOCK_NIX'] = environ['TMPDIR'] + '/nix_lock'

                Path(environ['CLAN_TEST_STORE'] + '/nix/store').mkdir(parents=True, exist_ok=True)
                Path(environ['CLAN_TEST_STORE'] + '/nix/var/nix/gcroots').mkdir(parents=True, exist_ok=True)

                if 'closureInfo' in environ:
                    # Read store paths from the closure info file
                    with open(environ['closureInfo'] + '/store-paths', 'r') as f:
                        store_paths = f.read().strip().split('\n')

                    # Copy store paths using absolute path to cp
                    subprocess.run(
                        ['${pkgs.coreutils}/bin/cp', '--recursive', '--target', environ['CLAN_TEST_STORE'] + '/nix/store'] + store_paths,
                        check=True
                    )

                    # Load the nix database using absolute path to nix-store
                    with open(environ['closureInfo'] + '/registration', 'r') as f:
                        subprocess.run(
                            ['${pkgs.nix}/bin/nix-store', '--load-db', '--store', environ['CLAN_TEST_STORE']],
                            input=f.read(),
                            text=True,
                            check=True
                        )
            EOF
            touch $out/${pkgs.python3.sitePackages}/py.typed
          '';

          doCheck = false;
        };
      };
    };
}
