{
  runCommand,
}:
let
  icons = fetchTarball {
    url = "https://git.clan.lol/clan/assets/archive/4442bace8898bcc3484d52cf076f24be6467d8f3.tar.gz";
    sha256 = "sha256:1gb7bd96sm7p232258kshkyjhw11hjrbpncxygrqnirfng777gxd";
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
