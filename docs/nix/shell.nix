{
  docs,
  pkgs,
  module-docs,
  clan-cli-docs,
  asciinema-player-js,
  asciinema-player-css,
  roboto,
  fira-code,
  self',
  ...
}:
pkgs.mkShell {
  name = "clan-docs";
  inputsFrom = [
    docs
    self'.devShells.default
  ];
  shellHook = ''
    git_root=$(git rev-parse --show-toplevel)
    cd ''${git_root}/docs

    mkdir -p ./site/reference/cli
    cp -af ${module-docs}/* ./site/reference/
    cp -af ${clan-cli-docs}/* ./site/reference/cli/

    chmod -R +w ./site/reference/*

    echo "Generated API documentation in './site/reference/' "

    mkdir -p ./site/static/asciinema-player

    ln -snf ${asciinema-player-js} ./site/static/asciinema-player/asciinema-player.min.js
    ln -snf ${asciinema-player-css} ./site/static/asciinema-player/asciinema-player.css

    # Link to fonts
    ln -snf ${roboto}/share/fonts/truetype/Roboto-Regular.ttf ./site/static/
    ln -snf ${fira-code}/share/fonts/truetype/FiraCode-VF.ttf ./site/static/
  '';
}
