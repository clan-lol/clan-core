{
  runCommand,
}:
let
  icons = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/02b659f77de8baeba1bd28c566fc04cfe5b7f682.tar.gz";
    sha256 = "sha256:1p6z8j2zp2i3ppm4f4lypy9gdw4abkc5bsnafdy14b7wr78sbrck";
  };
  assets = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/eb81db9ca168593d203b62e33914ffb904d59689.tar.gz";
    sha256 = "sha256:1b4zfblcdrbpdhljyp4xp24sk9nn4jj7lfiyxafpca86dafnvadm";
  };
in
runCommand "clan-site-assets" { } ''
  mkdir -p $out/icons
  cp -r ${assets}/* $out
  cp -r ${icons}/* $out/icons
''
