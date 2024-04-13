{ pkgs, ... }:
pkgs.stdenv.mkDerivation {
  name = "clan-documentation";

  src = ../.;

  nativeBuildInputs =
    [ pkgs.python3 ]
    ++ (with pkgs.python3Packages; [
      mkdocs
      mkdocs-material
    ]);

  buildPhase = ''
    mkdocs build --strict
    ls -la .
  '';

  installPhase = ''
    cp -a out/ $out/
  '';
}
