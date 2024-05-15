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
      ipdb
      pip
    ]);
in
mkShell {
  buildInputs = [
    nix-unit
    ruff
  ] ++ devshellTestDeps;

  PYTHONBREAKPOINT = "ipdb.set_trace";

  shellHook = ''
    export GIT_ROOT="$(git rev-parse --show-toplevel)"
    export PKG_ROOT="$GIT_ROOT/pkgs/clan-cli"

    # Add clan command to PATH
    export PATH="$PKG_ROOT/bin":"$PATH"

    # Needed for impure tests
    ln -sfT ${clan-cli.nixpkgs} "$PKG_ROOT/clan_cli/nixpkgs"
  '';
}
