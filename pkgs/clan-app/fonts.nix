{ fetchurl, runCommand }:
let
  # 400 -> Regular
  archivoRegular = fetchurl {
    url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/ArchivoSemiCondensed-Regular.woff2";
    hash = "sha256-3PeB6tMpbYxR9JFyQ+yjpM7bAvZIjcJ4eBiHr9iV5p4=";
  };
  # 500 -> Medium
  archivoMedium = fetchurl {
    url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/ArchivoSemiCondensed-Medium.woff2";
    hash = "sha256-IKaY3YhpmjMaIVUpwKRLd6eFiIihBoAP99I/pwmyll8=";
  };
  # 600 -> SemiBold
  archivoSemiBold = fetchurl {
    url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/ArchivoSemiCondensed-SemiBold.woff2";
    hash = "sha256-fOE+b+UeTRoj+sDdUWR1pPCZVn0ABy6FEDDmXrOA4LY=";
  };
in
runCommand "" { } ''
  mkdir -p $out
  cp ${archivoRegular} $out/ArchivoSemiCondensed-Regular.woff2
  cp ${archivoMedium} $out/ArchivoSemiCondensed-Medium.woff2
  cp ${archivoSemiBold} $out/ArchivoSemiCondensed-SemiBold.woff2
''
