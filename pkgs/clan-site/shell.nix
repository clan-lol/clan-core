{
  mkShellNoCC,
  clan-site,
  writeShellApplication,
  util-linux,
}:
mkShellNoCC {
  inputsFrom = [
    clan-site
  ];
  packages = [
    (writeShellApplication {
      name = "clan-site";
      runtimeInputs = [
        util-linux
      ];
      text = builtins.readFile ./clan-site.sh;
    })
  ];
  shellHook = ''
    ${clan-site.preBuild}
    chmod -R +w src/docs src/lib/assets
  '';
}
