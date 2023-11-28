{ clan-vm-manager, clan-cli, mkShell, ruff }:
mkShell {
  inherit (clan-vm-manager) propagatedBuildInputs buildInputs;
  nativeBuildInputs = [
    ruff
  ] ++ clan-vm-manager.nativeBuildInputs;

  shellHook = ''
    ln -sfT ${clan-cli.nixpkgs} ../clan-cli/clan_cli/nixpkgs

    export PYTHONBREAKPOINT=ipdb.set_trace

    # prepend clan-cli for development
    export PYTHONPATH=../clan-cli:$PYTHONPATH
  '';
}
