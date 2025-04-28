{
  lib,
  nix-unit,
  nix-select,
  clan-cli,
  mkShell,
  ruff,
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
      ]
      ++ (clan-cli.devshellPyDeps ps)
    ))
    ruff
    nix-unit
  ] ++ clan-cli.runtimeDependencies;

  inputsFrom = [ self'.devShells.default ];

  CLAN_PROVIDED_PACKAGES = lib.concatStringsSep ":" (
    lib.attrNames clan-cli.passthru.runtimeDependenciesMap
  );

  shellHook = ''
    export GIT_ROOT="$(git rev-parse --show-toplevel)"
    export PKG_ROOT="$GIT_ROOT/pkgs/clan-cli"
    export PYTHONWARNINGS=error

    export CLAN_CORE_PATH="$GIT_ROOT"

    # Add current package to PYTHONPATH
    export PYTHONPATH="$PKG_ROOT''${PYTHONPATH:+:$PYTHONPATH:}"

    # Add clan command to PATH
    export PATH="$PKG_ROOT/bin":"$PATH"

    # Needed for impure tests
    ln -sfT ${clan-cli.nixpkgs} "$PKG_ROOT/clan_cli/nixpkgs"
    ln -sfT ${nix-select} "$PKG_ROOT/clan_cli/select"

    # Generate classes.py from inventory schema
    # This file is in .gitignore
    ${self'.packages.classgen}/bin/classgen ${self'.legacyPackages.schemas.inventory-schema-abstract}/schema.json $PKG_ROOT/clan_cli/inventory/classes.py
  '';
}
