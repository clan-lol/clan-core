{ lib, stdenv, clan-vm-manager, gtk4, libadwaita, clan-cli, mkShell, ruff, desktop-file-utils, xdg-utils, mypy, python3Packages }:
mkShell {
  inherit (clan-vm-manager) propagatedBuildInputs buildInputs;

  linuxOnlyPackages = lib.optionals stdenv.isLinux [
    xdg-utils
  ];

  nativeBuildInputs = [
    ruff
    desktop-file-utils
    mypy
    python3Packages.ipdb
    gtk4.dev
    libadwaita.devdoc # has the demo called 'adwaita-1-demo'
  ] ++ clan-vm-manager.nativeBuildInputs;

  PYTHONBREAKPOINT = "ipdb.set_trace";

  shellHook = ''
    ln -sfT ${clan-cli.nixpkgs} ../clan-cli/clan_cli/nixpkgs

    # prepend clan-cli for development
    export PYTHONPATH=../clan-cli:$PYTHONPATH


    if ! command -v xdg-mime &> /dev/null; then
      echo "Warning: 'xdg-mime' is not available. The desktop file cannot be installed."
    fi

    # install desktop file
    set -eou pipefail
    DESKTOP_FILE_NAME=lol.clan.vm.manager.desktop
    DESKTOP_DST=~/.local/share/applications/$DESKTOP_FILE_NAME
    DESKTOP_SRC=${clan-vm-manager}/share/applications/$DESKTOP_FILE_NAME
    UI_BIN="${clan-vm-manager}/bin/clan-vm-manager"

    cp -f $DESKTOP_SRC $DESKTOP_DST
    sleep 2
    sed -i "s|Exec=.*clan-vm-manager|Exec=$UI_BIN|" $DESKTOP_DST
    xdg-mime default $DESKTOP_FILE_NAME  x-scheme-handler/clan
    echo "==== Validating desktop file installation   ===="
    set -x
    desktop-file-validate $DESKTOP_DST
    set +xeou pipefail
  '';
}
