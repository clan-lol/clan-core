{ clan-vm-manager, clan-cli, mkShell, ruff }:
mkShell {
  inherit (clan-vm-manager) propagatedBuildInputs buildInputs;
  nativeBuildInputs = [
    ruff
  ] ++ clan-vm-manager.nativeBuildInputs;

  PYTHONBREAKPOINT = "ipdb.set_trace";

  shellHook = ''
    ln -sfT ${clan-cli.nixpkgs} ../clan-cli/clan_cli/nixpkgs

    # prepend clan-cli for development
    export PYTHONPATH=../clan-cli:$PYTHONPATH

    set -euox
    # install desktop file
    cp -f ${clan-vm-manager}/share/applications/clan-vm-manager.desktop ~/.local/share/applications/clan-vm-manager.desktop
    sleep 2
    sed -i "s|Exec=.*clan-vm-manager|Exec=${clan-vm-manager}/bin/clan-vm-manager|" ~/.local/share/applications/clan-vm-manager.desktop
    xdg-mime default clan-vm-manager.desktop  x-scheme-handler/clan
    set +x
  '';
}
