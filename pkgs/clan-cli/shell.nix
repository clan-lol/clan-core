{ nix-unit, clan-cli, ui-assets, system, mkShell, writeScriptBin, openssh, ruff, python3 }:
let
  checkScript = writeScriptBin "check" ''
    nix build .#checks.${system}.{treefmt,clan-pytest} -L "$@"
  '';

  pythonWithDeps = python3.withPackages (
    ps:
    clan-cli.propagatedBuildInputs
    ++ clan-cli.devDependencies
    ++ [
      ps.pip
    ]
  );
in
mkShell {
  packages = [
    nix-unit
    openssh
    ruff
    clan-cli.checkPython
  ];

  shellHook = ''
    tmp_path=$(realpath ./.direnv)

    repo_root=$(realpath .)
    mkdir -p "$tmp_path/python/${pythonWithDeps.sitePackages}"

    # Install the package in editable mode
    # This allows executing `clan` from within the dev-shell using the current
    # version of the code and its dependencies.
    ${pythonWithDeps.interpreter} -m pip install \
      --quiet \
      --disable-pip-version-check \
      --no-index \
      --no-build-isolation \
      --prefix "$tmp_path/python" \
      --editable $repo_root

    rm -f clan_cli/nixpkgs clan_cli/webui/assets
    ln -sf ${clan-cli.nixpkgs} clan_cli/nixpkgs
    ln -sf ${ui-assets} clan_cli/webui/assets

    export PATH="$tmp_path/python/bin:${checkScript}/bin:$PATH"
    export PYTHONPATH="$repo_root:$tmp_path/python/${pythonWithDeps.sitePackages}:"


    export XDG_DATA_DIRS="$tmp_path/share''${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
    export fish_complete_path="$tmp_path/share/fish/vendor_completions.d''${fish_complete_path:+:$fish_complete_path}"
    mkdir -p \
      $tmp_path/share/fish/vendor_completions.d \
      $tmp_path/share/bash-completion/completions \
      $tmp_path/share/zsh/site-functions
    register-python-argcomplete --shell fish clan > $tmp_path/share/fish/vendor_completions.d/clan.fish
    register-python-argcomplete --shell bash clan > $tmp_path/share/bash-completion/completions/clan


    ./bin/clan flakes create example_clan
    ./bin/clan machines create example-machine example_clan
  '';
}
