{
  pkgs ? import <nixpkgs> {},
  system ? builtins.currentSystem,
}: let
  lib = pkgs.lib;
  python3 = pkgs.python3;
  package = import ./default.nix {
    inherit lib python3;
  };
  pythonWithDeps = python3.withPackages (
    ps:
      package.propagatedBuildInputs
      ++ package.devDependencies
      ++ [
        ps.pip
      ]
  );
  devShell = pkgs.mkShell {
    packages = [
      pkgs.ruff
      pythonWithDeps
    ];
    # sets up an editable install and add enty points to $PATH
    shellHook = ''
      tmp_path=$(realpath ./.pythonenv)
      repo_root=$(realpath .)
      if ! cmp -s pyproject.toml $tmp_path/pyproject.toml; then
          rm -rf $tmp_path
          mkdir -p "$tmp_path/${pythonWithDeps.sitePackages}"

          ${pythonWithDeps.interpreter} -m pip install \
          --quiet \
          --disable-pip-version-check \
          --no-index \
          --no-build-isolation \
          --prefix "$tmp_path" \
          --editable $repo_root && \
          cp -a pyproject.toml $tmp_path/pyproject.toml
      fi
      export PATH="$tmp_path/bin:$PATH"
      export PYTHONPATH="$repo_root:$tmp_path/${pythonWithDeps.sitePackages}"
    '';
  };
in
  devShell
