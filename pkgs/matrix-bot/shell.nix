{
  matrix-bot,
  mkShell,
  ruff,
  python3,
}:
let
  devshellTestDeps =
    matrix-bot.passthru.testDependencies
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

    ruff
  ] ++ devshellTestDeps;

  PYTHONBREAKPOINT = "ipdb.set_trace";

  shellHook = ''
    export GIT_ROOT="$(git rev-parse --show-toplevel)"
    export PKG_ROOT="$GIT_ROOT/pkgs/matrix-bot"

    # Add clan command to PATH
    export PATH="$PKG_ROOT/bin":"$PATH"
  '';
}
