{
  buildNpmPackage,
  importNpmLock,
  nodejs_24,
  docs-markdowns,
}:
buildNpmPackage (finalAttrs: {
  pname = "clan-site";
  version = "0.0.1";
  nodejs = nodejs_24;
  src = ./.;

  npmDeps = importNpmLock {
    npmRoot = ./.;
  };

  npmConfigHook = importNpmLock.npmConfigHook;

  preBuild = ''
    mkdir -p src/docs
    cp -r ${docs-markdowns}/* src/docs
    chmod -R +w src/docs

    mkdir -p src/lib/assets/icons
    cp -af ${../clan-app/ui/src/assets/icons}/* src/lib/assets/icons
    chmod -R +w src/lib/assets/icons
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
          ;
        npmBuildScript = "lint";
      };
    };
  };
})
