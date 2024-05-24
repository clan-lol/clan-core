{
  pkgs,
  module-docs,
  clan-cli-docs,
  asciinema-player-js,
  asciinema-player-css,
  ...
}:
let
  uml-c4 = pkgs.python3Packages.plantuml-markdown.override { plantuml = pkgs.plantuml-c4; };
in
pkgs.stdenv.mkDerivation {
  name = "clan-documentation";

  src = ../.;

  nativeBuildInputs =
    [
      pkgs.python3
      uml-c4
    ]
    ++ (with pkgs.python3Packages; [
      mkdocs
      mkdocs-material
      mkdocs-rss-plugin
      mkdocs-macros
    ]);
  configurePhase = ''
    mkdir -p ./site/reference/cli
    cp -af ${module-docs}/* ./site/reference/
    cp -af ${clan-cli-docs}/* ./site/reference/cli/

    mkdir -p ./site/static/asciinema-player
    ln -snf ${asciinema-player-js} ./site/static/asciinema-player/asciinema-player.min.js
    ln -snf ${asciinema-player-css} ./site/static/asciinema-player/asciinema-player.css
  '';

  buildPhase = ''
    mkdocs build --strict
    ls -la .
  '';

  installPhase = ''
    cp -a out/ $out/
  '';
}
