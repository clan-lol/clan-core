{
  buildNpmPackage,
  nodejs_22,
  importNpmLock,

  clan-ts-api,
  fonts,
}:
buildNpmPackage {
  pname = "clan-app-ui";
  version = "0.0.1";
  nodejs = nodejs_22;
  src = ./ui;

  npmDeps = importNpmLock {
    npmRoot = ./ui;
  };
  npmConfigHook = importNpmLock.npmConfigHook;

  preBuild = ''
    mkdir -p api
    cp -r ${clan-ts-api}/* api
    cp -r ${fonts} ".fonts"
  '';
}
