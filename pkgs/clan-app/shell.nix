{
  lib,
  stdenv,
  clan-app,
  mkShell,
  ruff,
  webview-lib,
  clan-app-ui,
  clan-ts-api,
  clan-lib-openapi,
  ps,
  fetchzip,
  process-compose,
  json2ts,
  playwright-driver,
  luakit,
  self',
}:
let
  GREEN = "\\033[1;32m";
  NC = "\\033[0m";

  swagger-ui-dist = fetchzip {
    url = "https://github.com/swagger-api/swagger-ui/archive/refs/tags/v5.26.2.zip";
    sha256 = "sha256-KoFOsCheR1N+7EigFDV3r7frMMQtT43HE5H1/xsKLG4=";
  };

in

mkShell {
  name = "ui";

  inputsFrom = [
    self'.devShells.default
    clan-app-ui
  ];

  packages = [
    # required for reload-python-api.sh script
    json2ts
  ]
  ++ (lib.optionals stdenv.hostPlatform.isLinux [
    # for viewing the storybook in a webkit-based browser to match webview
    luakit
  ]);

  inherit (clan-app) propagatedBuildInputs;

  nativeBuildInputs = clan-app.nativeBuildInputs ++ [
    ps
    process-compose
  ];

  buildInputs = [
    (clan-app.pythonRuntime.withPackages (
      ps:
      with ps;
      [
        mypy
        pytest-cov
      ]
      ++ (clan-app.devshellPyDeps ps)
    ))
    ruff
  ]
  ++ clan-app.runtimeDeps;

  shellHook = ''
    export CLAN_CORE_PATH=$(git rev-parse --show-toplevel)

    ## Clan app
    pushd "$CLAN_CORE_PATH/pkgs/clan-app"

    # Add clan-app command to PATH
    export PATH="$(pwd)/bin":"$PATH"

    # Add current package to PYTHONPATH
    export PYTHONPATH="$(pwd)''${PYTHONPATH:+:$PYTHONPATH:}"
    popd

    # Add clan-cli to the python path so that we can import it without building it in nix first
    export PYTHONPATH="$CLAN_CORE_PATH/pkgs/clan-cli":"$PYTHONPATH"

    export XDG_DATA_DIRS=$GSETTINGS_SCHEMAS_PATH:$XDG_DATA_DIRS
    export WEBVIEW_LIB_DIR=${webview-lib}/lib
    export OPENAPI_FILE="${clan-lib-openapi}"
    export SWAGGER_UI_DIST="${swagger-ui-dist}/dist"

    ## Webview UI
    # Add clan-app-ui scripts to PATH
    pushd "$CLAN_CORE_PATH/pkgs/clan-app/ui"
    export NODE_PATH="$(pwd)/node_modules"
    export PATH="$NODE_PATH/.bin:$(pwd)/bin:$PATH"

    rm -rf .fonts || true
    cp -r ${self'.packages.fonts} .fonts
    chmod -R +w .fonts
    mkdir -p api
    cp -r ${clan-ts-api}/* api
    chmod -R +w api
    popd

    # configure process-compose
    if test -f "$CLAN_CORE_PATH/pkgs/clan-app/.local.env"; then
      source "$CLAN_CORE_PATH/pkgs/clan-app/.local.env"
    fi

    export PC_CONFIG_FILES="$CLAN_CORE_PATH/pkgs/clan-app/process-compose.yaml"

    echo -e "${GREEN}To launch a qemu VM for testing, run:\n  start-vm <number of VMs>${NC}"
  ''
  +
    # todo darwin support needs some work
    (lib.optionalString stdenv.hostPlatform.isLinux ''
      # configure playwright for storybook snapshot testing
      # we only want webkit as that matches what the app is rendered with

      export PLAYWRIGHT_BROWSERS_PATH=${
        playwright-driver.browsers.override {
          withFfmpeg = false;
          withFirefox = false;
          withWebkit = true;
          withChromium = false;
          withChromiumHeadlessShell = true;
        }
      }

      # stop playwright from trying to validate it has downloaded the necessary browsers
      # we are providing them manually via nix

      export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true

      # playwright browser drivers are versioned e.g. webkit-2191
      # this helps us avoid having to update the playwright js dependency everytime we update nixpkgs and vice versa
      # see vitest.config.js for corresponding launch configuration

      export PLAYWRIGHT_CHROMIUM_EXECUTABLE=$(find -L "$PLAYWRIGHT_BROWSERS_PATH" -type f -name "headless_shell")
    '');
}
