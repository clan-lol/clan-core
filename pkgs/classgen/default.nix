{
  stdenv,
  python3,
  lib,
}:

stdenv.mkDerivation {
  name = "classgen";
  src = ./.;
  buildInputs = [ python3 ];
  installPhase = ''
    install -Dm755 ${./main.py} $out/bin/classgen
  '';
  meta = with lib; {
    description = "A tool to generate Python dataclasses from JSON Schema definitions";
    license = licenses.mit;
  };
}
