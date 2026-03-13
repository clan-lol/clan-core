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
    export PRJ_ROOT=$(git rev-parse --show-toplevel)
    export CLAN_SITE_DIR=$PRJ_ROOT/pkgs/clan-site
    cd $CLAN_SITE_DIR
    ${clan-site.preBuild}
  '';
}
