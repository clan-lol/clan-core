{
  lib,
  nix-unit,
  clan-cli,
  mkShell,
  ruff,
  self,
  self',
}:

mkShell {
  name = "clan-cli";
  buildInputs = [
    (clan-cli.pythonRuntime.withPackages (
      ps:
      with ps;
      [
        mypy
        pytest-cov
      ]
      ++ (clan-cli.devshellPyDeps ps)
    ))
    ruff
    nix-unit
  ]
  ++ clan-cli.runtimeDependencies
  ++ clan-cli.testRuntimeDependencies;

  inputsFrom = [ self'.devShells.default ];

  CLAN_PROVIDED_PACKAGES = lib.concatStringsSep ":" (
    lib.attrNames clan-cli.passthru.runtimeDependenciesMap
  );

  shellHook = ''
    export GIT_ROOT="$(git rev-parse --show-toplevel)"
    export PKG_ROOT="$GIT_ROOT/pkgs/clan-cli"
    export PYTHONWARNINGS=error

    export CLAN_CORE_PATH="$GIT_ROOT"

     # used for tests without flakes
    export NIXPKGS=${self.inputs.nixpkgs.outPath}
    export NIX_SELECT=${self.inputs.nix-select.outPath}

    # Add current package to PYTHONPATH
    export PYTHONPATH="$PKG_ROOT''${PYTHONPATH:+:$PYTHONPATH:}"

    # Add clan command to PATH
    export PATH="$PKG_ROOT/bin":"$PATH"
  '';
}
