{
  mkShell,
  python3,
  iproute2,
  ruff,
}:

mkShell {
  name = "network-status";

  packages = [
    (python3.withPackages (ps: [
      ps.pytest
      ps.mypy
    ]))
    iproute2
    ruff
  ];

  shellHook = ''
    export GIT_ROOT="$(git rev-parse --show-toplevel)"
    export PKG_ROOT="$GIT_ROOT/pkgs/network-status"

    # Add current package to PYTHONPATH for testing
    export PYTHONPATH="$PKG_ROOT''${PYTHONPATH:+:$PYTHONPATH}"

    # Add script to PATH for testing
    export PATH="$PKG_ROOT:$PATH"
  '';
}
