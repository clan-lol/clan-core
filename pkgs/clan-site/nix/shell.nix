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
    ${clan-site.preBuild}
    chmod -R +w src/docs src/lib/assets
  '';
}
