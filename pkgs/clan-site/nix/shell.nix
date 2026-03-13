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
    cd $PRJ_ROOT/pkgs/clan-site
    ${clan-site.preBuild}
  '';
}
