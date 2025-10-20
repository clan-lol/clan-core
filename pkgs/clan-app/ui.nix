{
  buildNpmPackage,
  nodejs_22,
  importNpmLock,
  clan-ts-api,
  fonts,
  ps,
  playwright-driver,
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

    # only needed for the next couple weeks to make sure this file doesn't make it back into the git history
    if [[ -f "${./ui}/src/routes/Onboarding/background.jpg" ]]; then
        echo "background.jpg found, exiting"
        exit 1
    fi
  '';

  # todo figure out why this fails only inside of Nix
  # Something about passing orientation in any of the Form stories is causing the browser to crash
  # `npm run test-storybook-static` works fine in the devshell

  passthru = {
    storybook = buildNpmPackage {
      pname = "${finalAttrs.pname}-storybook";
      inherit (finalAttrs)
        version
        nodejs
        src
        npmDeps
        npmConfigHook
        ;

      nativeBuildInputs = finalAttrs.nativeBuildInputs ++ [
        ps
      ];

      npmBuildScript = "test-storybook";

      env = {
        PLAYWRIGHT_BROWSERS_PATH = "${playwright-driver.browsers.override {
          withFfmpeg = false;
          withFirefox = false;
          withWebkit = true;
          withChromium = false;
          withChromiumHeadlessShell = false;
        }}";
        PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = true;
      };
    };
  };
})
