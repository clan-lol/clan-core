{
  fetchurl,
  fetchzip,
  runCommand,
}:
let

  archivo = {
    # 400 -> Regular
    regular = fetchurl {
      url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/Archivo-Regular.woff2";
      hash = "sha256-sxWvVJvHnZgKvgvKCmSOz6AQa+G/IFv57YCeY4HyTQo=";
    };

    # 500 -> Medium
    medium = fetchurl {
      url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/Archivo-Medium.woff2";
      hash = "sha256-FalQLFry4jdHwuMr1zmxyG7UuI1rn1pd2cV8tmJetRs=";
    };

    # 600 -> SemiBold
    semiBold = fetchurl {
      url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/Archivo-SemiBold.woff2";
      hash = "sha256-XrTdFFUNLIdxwgqJB/sX8Om89XqgF/vCz1cYl7I6QTU=";
    };
  };

  archivoSemi = {
    # 400 -> Regular
    regular = fetchurl {
      url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/ArchivoSemiCondensed-Regular.woff2";
      hash = "sha256-3PeB6tMpbYxR9JFyQ+yjpM7bAvZIjcJ4eBiHr9iV5p4=";
    };

    # 500 -> Medium
    medium = fetchurl {
      url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/ArchivoSemiCondensed-Medium.woff2";
      hash = "sha256-IKaY3YhpmjMaIVUpwKRLd6eFiIihBoAP99I/pwmyll8=";
    };

    # 600 -> SemiBold
    semiBold = fetchurl {
      url = "https://github.com/Omnibus-Type/Archivo/raw/b5d63988ce19d044d3e10362de730af00526b672/fonts/webfonts/ArchivoSemiCondensed-SemiBold.woff2";
      hash = "sha256-fOE+b+UeTRoj+sDdUWR1pPCZVn0ABy6FEDDmXrOA4LY=";
    };
  };

  firaCode = fetchzip {
    url = "https://github.com/tonsky/FiraCode/releases/download/6.2/Fira_Code_v6.2.zip";
    stripRoot = false;
    hash = "sha256-UHOwZL9WpCHk6vZaqI/XfkZogKgycs5lWg1p0XdQt0A=";
  };

in
runCommand "" { } ''
  mkdir -p $out

  cp ${archivo.regular} $out/Archivo-Regular.woff2
  cp ${archivo.medium} $out/Archivo-Medium.woff2
  cp ${archivo.semiBold} $out/Archivo-SemiBold.woff2

  cp ${archivoSemi.regular} $out/ArchivoSemiCondensed-Regular.woff2
  cp ${archivoSemi.medium} $out/ArchivoSemiCondensed-Medium.woff2
  cp ${archivoSemi.semiBold} $out/ArchivoSemiCondensed-SemiBold.woff2

  cp ${firaCode}/woff2/FiraCode-Regular.woff2 $out/FiraCode-Regular.woff2
''
