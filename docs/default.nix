{ pkgs, ... }:
pkgs.stdenv.mkDerivation {
  name = "clan-documentation";

  src = ./.;

  nativeBuildInputs =
    [ pkgs.python3 ]
    ++ (with pkgs.python3Packages; [
      mkdocs
      mkdocs-material
      mkdocs-drawio-exporter
      mkdocs-swagger-ui-tag
      plantuml-markdown
    ]);

  buildPhase = ''
    mkdocs build --strict

    ls -la .
  '';

  installPhase = ''
    cp -a site/ $out/
  '';
}
