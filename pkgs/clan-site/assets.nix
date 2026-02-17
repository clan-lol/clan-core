{
  runCommand,
}:
let
  icons = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/3112e8cbc9ad0b3d88ab47177baf19e3a3e2fea6.tar.gz";
    sha256 = "sha256:1dimcy2kmmq1nx239d272r6hrbmvri9qjcdzymvhhpdmflfa5rhv";
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
