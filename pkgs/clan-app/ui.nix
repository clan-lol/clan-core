{
  buildNpmPackage,
  nodejs_22,
  importNpmLock,
  clan-ts-api,
  fonts,
}:
buildNpmPackage (_finalAttrs: {
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

  # todo figure out why this fails only inside of Nix
  # Something about passing orientation in any of the Form stories is causing the browser to crash
  # `npm run test-storybook-static` works fine in the devshell
  #
  #  passthru = rec {
  #    storybook = buildNpmPackage {
  #      pname = "${finalAttrs.pname}-storybook";
  #      inherit (finalAttrs)
  #        version
  #        nodejs
  #        src
  #        npmDeps
  #        npmConfigHook
  #        preBuild
  #        ;
  #
  #      nativeBuildInputs = finalAttrs.nativeBuildInputs ++ [
  #        ps
  #      ];
  #
  #      npmBuildScript = "test-storybook-static";
  #
  #      env = finalAttrs.env // {
  #        PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = 1;
  #        PLAYWRIGHT_BROWSERS_PATH = "${playwright-driver.browsers.override {
  #          withChromiumHeadlessShell = true;
  #        }}";
  #        PLAYWRIGHT_HOST_PLATFORM_OVERRIDE = "ubuntu-24.04";
  #      };
  #
  #      postBuild = ''
  #        mv storybook-static $out
  #      '';
  #    };
  #  };
})
