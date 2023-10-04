{ nix-unit, clan-cli, ui-assets, system, mkShell, writeScriptBin, openssh }:
let
  checkScript = writeScriptBin "check" ''
    nix build .#checks.${system}.{treefmt,clan-pytest} -L "$@"
  '';
in
mkShell {
  packages = [
    nix-unit
    openssh
    clan-cli.checkPython
  ];

  shellHook = ''
    tmp_path=$(realpath ./.direnv)

    rm -f clan_cli/nixpkgs clan_cli/webui/assets
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

    ./bin/clan machines create example
  '';
}
