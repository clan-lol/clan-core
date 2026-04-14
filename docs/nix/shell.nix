{
  mkShellNoCC,
  clan-site,
  clan-site-cli,
}:
mkShellNoCC {
  inputsFrom = [
    clan-site
  ];
  packages = [
    clan-site-cli
  ];
  env = clan-site.devShellEnv;
  shellHook = ''
    cd ../pkgs/clan-site
    export CLAN_SITE_DIR="$PWD"
    ${clan-site.devShellHook}
    echo "Run 'clan-site' to start the live docs server"
  '';
}
