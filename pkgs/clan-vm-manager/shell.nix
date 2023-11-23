{ clan-vm-manager, clan-cli, mkShell, ruff, python3 }:
let
  pythonWithDeps = python3.withPackages (ps: clan-vm-manager.propagatedBuildInputs);
in
mkShell {
  buildInputs = [ pythonWithDeps ] ++ clan-vm-manager.buildInputs;
  nativeBuildInputs = [
    ruff
  ] ++ clan-vm-manager.nativeBuildInputs;

  shellHook = ''
    rm -f ../clan-cli/clan_cli/nixpkgs
    ln -sf ${clan-cli.nixpkgs} ../clan-cli/clan_cli/nixpkgs
  '';
}
