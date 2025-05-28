{
  buildNpmPackage,
  nodejs_22,
  importNpmLock,
  clan-ts-api,
  playwright-driver,
  ps,
  fonts,
}:
buildNpmPackage (finalAttrs: {
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

  passthru = rec {
    storybook = buildNpmPackage {
      pname = "${finalAttrs.pname}-storybook";
      inherit (finalAttrs)
        version
        nodejs
        src
        npmDeps
        npmConfigHook
        preBuild
        ;

      nativeBuildInputs = finalAttrs.nativeBuildInputs ++ [
        ps
      ];

      npmBuildScript = "test-storybook-static";

      env = finalAttrs.env // {
        PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = 1;
        PLAYWRIGHT_BROWSERS_PATH = "${playwright-driver.browsers.override {
          withChromiumHeadlessShell = true;
        }}";
        PLAYWRIGHT_HOST_PLATFORM_OVERRIDE = "ubuntu-24.04";
      };

      postBuild = ''
        mv storybook-static $out
      '';
    };
  };
})
