{ pkgs, module-docs, ... }:
pkgs.stdenv.mkDerivation {
  name = "clan-documentation";

  src = ../.;

  nativeBuildInputs =
    [ pkgs.python3 ]
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
