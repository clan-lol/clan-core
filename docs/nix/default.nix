{ pkgs, module-docs, ... }:
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
    ]);
  configurePhase = ''
    mkdir -p ./site/reference
    cp -af ${module-docs}/* ./site/reference/

  '';

  buildPhase = ''
    mkdocs build --strict
    ls -la .
  '';

  installPhase = ''
    cp -a out/ $out/
  '';
}
