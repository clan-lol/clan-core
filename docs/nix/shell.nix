{
  docs,
  pkgs,
  module-docs,
  clan-cli-docs,
  asciinema-player-js,
  asciinema-player-css,
  ...
}:
pkgs.mkShell {
  inputsFrom = [ docs ];
  shellHook = ''
    mkdir -p ./site/reference/cli
    cp -af ${module-docs}/* ./site/reference/
    cp -af ${clan-cli-docs}/* ./site/reference/cli/
    chmod +w ./site/reference/*

    echo "Generated API documentation in './site/reference/' "

    mkdir -p ./site/static/asciinema-player
    ln -snf ${asciinema-player-js} ./site/static/asciinema-player/asciinema-player.min.js
    ln -snf ${asciinema-player-css} ./site/static/asciinema-player/asciinema-player.css
  '';
}
