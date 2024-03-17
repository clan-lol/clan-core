{
  perSystem =
    {
      pkgs,
      self',
      lib,
      ...
    }:
    let
      python3 = pkgs.python3;
      pypkgs = python3.pkgs;
      clan-cli = self'.packages.clan-cli;
      clan-vm-manager = self'.packages.clan-vm-manager;
      pythonWithDeps = python3.withPackages (
        ps:
        clan-cli.propagatedBuildInputs
        ++ clan-cli.devDependencies
        ++ [
          ps.pip
          # clan-vm-manager deps
          ps.pygobject3
        ]
      );
      linuxOnlyPackages = lib.optionals pkgs.stdenv.isLinux [ pkgs.xdg-utils ];
    in
    {
      devShells.python = pkgs.mkShell {
        inputsFrom = [ self'.devShells.default ];
        packages =
          [
            pythonWithDeps
            pypkgs.mypy
            pypkgs.ipdb
            pkgs.desktop-file-utils
            pkgs.gtk4.dev
            pkgs.ruff
            pkgs.libadwaita.devdoc # has the demo called 'adwaita-1-demo'
          ]
          ++ linuxOnlyPackages
          ++ clan-vm-manager.nativeBuildInputs
          ++ clan-vm-manager.buildInputs
          ++ clan-cli.nativeBuildInputs;

        PYTHONBREAKPOINT = "ipdb.set_trace";

        shellHook = ''
          ln -sfT ${clan-cli.nixpkgs} ./pkgs/clan-cli/clan_cli/nixpkgs

          ## PYTHON

          tmp_path="$(realpath ./.direnv/python)"
          repo_root=$(realpath .)
          mkdir -p "$tmp_path/${pythonWithDeps.sitePackages}"

          # local dependencies
          localPackages=(
            $repo_root/pkgs/clan-cli
            $repo_root/pkgs/clan-vm-manager
          )

          # Install executable wrappers for local python packages scripts
          # This is done by utilizing `pip install --editable`
          # As a result, executables like `clan` can be executed from within the dev-shell
          # while using the current version of the code and its dependencies.
          for package in "''${localPackages[@]}"; do
            pname=$(basename "$package")
            if
              [ ! -e "$tmp_path/meta/$pname/pyproject.toml" ] \
              || [ ! -e "$package/pyproject.toml" ] \
              || ! cmp -s "$tmp_path/meta/$pname/pyproject.toml" "$package/pyproject.toml"
            then
              echo "==== Installing local python package $pname in editable mode ===="
              mkdir -p "$tmp_path/meta/$pname"
              cp $package/pyproject.toml $tmp_path/meta/$pname/pyproject.toml
              ${python3.pkgs.pip}/bin/pip install \
                --quiet \
                --disable-pip-version-check \
                --no-index \
                --no-build-isolation \
                --prefix "$tmp_path" \
                --editable "$package"
            fi
          done

          export PATH="$tmp_path/bin:$PATH"
          export PYTHONPATH="''${PYTHONPATH:+$PYTHONPATH:}$tmp_path/${pythonWithDeps.sitePackages}"

          for package in "''${localPackages[@]}"; do
            export PYTHONPATH="$package:$PYTHONPATH"
          done



          ## GUI

          if ! command -v xdg-mime &> /dev/null; then
            echo "Warning: 'xdg-mime' is not available. The desktop file cannot be installed."
          fi

          # install desktop file
          set -eou pipefail
          DESKTOP_FILE_NAME=org.clan.vm-manager.desktop
          DESKTOP_DST=~/.local/share/applications/$DESKTOP_FILE_NAME
          DESKTOP_SRC=${clan-vm-manager.desktop-file}/share/applications/$DESKTOP_FILE_NAME
          UI_BIN="clan-vm-manager"

          cp -f $DESKTOP_SRC $DESKTOP_DST
          sed -i "s|Exec=.*clan-vm-manager|Exec=$UI_BIN|" $DESKTOP_DST
          xdg-mime default $DESKTOP_FILE_NAME  x-scheme-handler/clan
          echo "==== Validating desktop file installation   ===="
          set -x
          desktop-file-validate $DESKTOP_DST
          set +xeou pipefail
        '';
      };
    };
}
