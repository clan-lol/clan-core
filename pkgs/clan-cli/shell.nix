{
  nix-unit,
  clan-cli,
  mkShell,
  ruff,
  python3,
}:
let
  devshellTestDeps =
    clan-cli.passthru.testDependencies
    ++ (with python3.pkgs; [
      rope
      setuptools
      wheel
      pip
    ]);
in
mkShell {
  buildInputs = [
    nix-unit
    ruff
  ] ++ devshellTestDeps;

  shellHook = ''
    export PATH=$(pwd)/bin:$PATH

    ln -sfT ${clan-cli.nixpkgs} clan_cli/nixpkgs
  '';
}
