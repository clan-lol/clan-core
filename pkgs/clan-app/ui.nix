{
  buildNpmPackage,
  nodejs_22,
  importNpmLock,
  clan-ts-api,
  fonts,
  ps,
  jq,
  playwright,
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
    tests = {
      "${finalAttrs.pname}-storybook" = buildNpmPackage {
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
          jq
        ];

        npmBuildScript = "test-storybook";

        env = {
          PLAYWRIGHT_BROWSERS_PATH = "${playwright.browsers.override {
            withFfmpeg = false;
            withFirefox = false;
            withWebkit = true;
            withChromium = false;
            withChromiumHeadlessShell = false;
          }}";
          PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS = true;
          # This is needed to disable revisionOverrides in browsers.json which
          # the playwright nix package does not support:
          # https://github.com/NixOS/nixpkgs/blob/f9c3b27aa3f9caac6717973abcc549dbde16bdd4/pkgs/development/web/playwright/driver.nix#L261
          PLAYWRIGHT_HOST_PLATFORM_OVERRIDE = "nixos";
        };
        preBuild = finalAttrs.preBuild + ''
          playwright_ver=$(jq --raw-output .devDependencies.playwright ${./ui/package.json})
          if [[ $playwright_ver != '${playwright.version}' ]]; then
            echo >&2 "playwright npm package version ($playwright_ver) is different from that from the nixpkgs (${playwright.version})"
            echo >&2 "Run this command to update the npm package version"
            echo >&2
            echo >&2 "  npm i -D --save-exact playwright@${playwright.version}"
            echo >&2
            exit 1
          fi
        '';
      };
    };
  };
})
