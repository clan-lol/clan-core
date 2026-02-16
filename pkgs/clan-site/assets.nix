{
  runCommand,
}:
let
  icons = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/36d2187f4e1fee7674a4cd8698accc1e466d2acf.tar.gz";
    sha256 = "sha256:0zpvbz8l1j7sr23662akj7h25r6k4br632q3v6q5y9m0qdhwnd89";
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
