{
  runCommand,
}:
let
  icons = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/02b659f77de8baeba1bd28c566fc04cfe5b7f682.tar.gz";
    sha256 = "sha256:1p6z8j2zp2i3ppm4f4lypy9gdw4abkc5bsnafdy14b7wr78sbrck";
  };
  assets = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/1347b6d6ec02fbc94e99cbb2acc8a05ec52a26ba.tar.gz";
    sha256 = "sha256:0gk0d81d7fsghdhig5whxx7ymdn5cjc73jw7vfyhird4sq964wix";
  };
in
runCommand "clan-site-assets" { } ''
  mkdir -p $out/icons
  cp -r ${assets}/* $out
  cp -r ${icons}/* $out/icons
''
