{
  runCommand,
}:
let
  icons = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/0f8a9d6e2177eda598807cd69708e04ec7a38c94.tar.gz";
    sha256 = "sha256:1ayy7q2is6bflwkmmmf1g988i4s18fx1ayc5kifzfhqilax1ygjg";
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
