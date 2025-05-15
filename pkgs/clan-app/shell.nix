{
  clan-app,
  mkShell,
  ruff,
  webview-lib,
  webview-ui,
  clan-ts-api,
  process-compose,
  python3,
  json2ts,
  self',
}:

mkShell {
  name = "ui";

  inputsFrom = [
    self'.devShells.default
    webview-ui
  ];

  packages = [
    # required for reload-python-api.sh script
    python3
    json2ts
  ];

  inherit (clan-app) propagatedBuildInputs;

  nativeBuildInputs = clan-app.nativeBuildInputs ++ [
    process-compose
  ];

  buildInputs = [
    (clan-app.pythonRuntime.withPackages (
      ps:
      with ps;
      [
        mypy
      ]
      ++ (clan-app.devshellPyDeps ps)
    ))
    ruff
  ] ++ clan-app.runtimeDeps;

  shellHook = ''
    export GIT_ROOT=$(git rev-parse --show-toplevel)

    export CLAN_CORE_PATH="$GIT_ROOT"

    export PKG_ROOT_UI="$GIT_ROOT/pkgs/ui"
    export PKG_ROOT_CLAN_APP="$PKG_ROOT_UI"/clan-app
    export PKG_ROOT_WEBVIEW_UI="$PKG_ROOT_UI"/webview-ui

    export NODE_PATH="$PKG_ROOT_WEBVIEW_UI/app/node_modules"

    # Add current package to PYTHONPATH
    export PYTHONPATH="$PKG_ROOT_CLAN_APP''${PYTHONPATH:+:$PYTHONPATH:}"

    # Add clan-app command to PATH
    export PATH="$PKG_ROOT_CLAN_APP/bin":"$PATH"

    # Add webview-ui scripts to PATH
    scriptsPath="$PKG_ROOT/bin"
    export PATH="$NODE_PATH/.bin:$scriptsPath:$PATH"

    # Add clan-cli to the python path so that we can import it without building it in nix first
    export PYTHONPATH="$GIT_ROOT/pkgs/clan-cli":"$PYTHONPATH"

    export XDG_DATA_DIRS=$GSETTINGS_SCHEMAS_PATH:$XDG_DATA_DIRS

    export WEBVIEW_LIB_DIR=${webview-lib}/lib
    source $PKG_ROOT_CLAN_APP/.local.env

    cp -r ${self'.packages.fonts} "$PKG_ROOT_WEBVIEW_UI/app/.fonts"
    chmod -R +w "$PKG_ROOT_WEBVIEW_UI/app/.fonts"

    # Define the yellow color code
    YELLOW='\033[1;33m'
    # Define the reset color code
    NC='\033[0m'

    mkdir -p "$PKG_ROOT_WEBVIEW_UI/app/api"
    cp -r ${clan-ts-api}/* "$PKG_ROOT_WEBVIEW_UI/app/api"
    chmod -R +w "$PKG_ROOT_WEBVIEW_UI/app/api"

    # configure process-compose
    export PC_CONFIG_FILES="$PKG_ROOT_UI/process-compose.yaml"
  '';
}
