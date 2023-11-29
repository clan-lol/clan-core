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
  '';
}
