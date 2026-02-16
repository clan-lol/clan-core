{
  buildNpmPackage,
  importNpmLock,
  nodejs_24,
  docs-markdowns,
  clan-site-assets,
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
    mkdir -p src/docs src/lib/assets
    cp -r ${docs-markdowns}/* src/docs
    cp -r ${clan-site-assets}/* src/lib/assets
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
