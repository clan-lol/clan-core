{
  buildNpmPackage,
  importNpmLock,
  nodejs_latest,
  docs-markdowns,
}:
buildNpmPackage (finalAttrs: {
  pname = "clan-site";
  version = "0.0.1";
  nodejs = nodejs_latest;
  src = ./.;

  npmDeps = importNpmLock {
    npmRoot = ./.;
  };

  npmConfigHook = importNpmLock.npmConfigHook;

  preBuild = ''
    mkdir -p src/docs
    cp -r ${docs-markdowns}/* src/docs
    chmod -R +w src/docs
    mv src/docs/reference/index.md src/docs/reference.md

    mkdir -p src/lib/assets/icons
    cp -af ${../clan-app/ui/src/assets/icons}/* src/lib/assets/icons
  '';
  passthru = {
    tests = {
      "${finalAttrs.pname}-lint" = buildNpmPackage {
        name = "${finalAttrs.pname}-lint";
        inherit (finalAttrs)
          nodejs
          src
          npmDeps
          npmConfigHook
          preBuild
          ;
        npmBuildScript = "lint";
      };
    };
  };
})
