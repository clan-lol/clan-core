{ nix-unit, clan-cli, ui-assets, python3, system, ruff, mkShell, writeScriptBin }:
let
  pythonWithDeps = python3.withPackages (
    ps:
    clan-cli.propagatedBuildInputs
    ++ clan-cli.devDependencies
    ++ [
      ps.pip
    ]
  );
  checkScript = writeScriptBin "check" ''
    nix build .#checks.${system}.{treefmt,clan-pytest} -L "$@"
  '';
in
mkShell {
  packages = [
    ruff
    nix-unit
    pythonWithDeps
  ];
  # sets up an editable install and add enty points to $PATH
  # This provides dummy options for testing clan config and prevents it from
  # evaluating the flake .#
  CLAN_OPTIONS_FILE = ./clan_cli/config/jsonschema/options.json;
  PYTHONPATH = "${pythonWithDeps}/${pythonWithDeps.sitePackages}";
  shellHook = ''
    tmp_path=$(realpath ./.direnv)

    rm -f clan_cli/nixpkgs clan_cli/assets
    ln -sf ${clan-cli.nixpkgs} clan_cli/nixpkgs
    ln -sf ${ui-assets} clan_cli/webui/assets

    export PATH="$tmp_path/bin:${checkScript}/bin:$PATH"
    export PYTHONPATH="$PYTHONPATH:$(pwd)"

    export XDG_DATA_DIRS="$tmp_path/share''${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
    export fish_complete_path="$tmp_path/share/fish/vendor_completions.d''${fish_complete_path:+:$fish_complete_path}"
    mkdir -p \
      $tmp_path/share/fish/vendor_completions.d \
      $tmp_path/share/bash-completion/completions \
      $tmp_path/share/zsh/site-functions
    register-python-argcomplete --shell fish clan > $tmp_path/share/fish/vendor_completions.d/clan.fish
    register-python-argcomplete --shell bash clan > $tmp_path/share/bash-completion/completions/clan

    ${clan-cli}/bin/clan machines create example
  '';
}
