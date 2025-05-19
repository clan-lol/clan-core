{
  clan-app,
  mkShell,
  ruff,
  webview-lib,
  clan-app-ui,
  clan-ts-api,
  process-compose,
  json2ts,
  self',
}:
let
  GREEN = "\\033[1;32m";
  NC = "\\033[0m";
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
    export CLAN_CORE_PATH=$(git rev-parse --show-toplevel)

    ## Clan app
    # Add clan-app command to PATH
    pushd "$CLAN_CORE_PATH/pkgs/clan-app"
    export PATH="$(pwd)/bin":"$PATH"
    # Add current package to PYTHONPATH
    export PYTHONPATH="$(pwd)/pkgs/clan-app/''${PYTHONPATH:+:$PYTHONPATH:}"
    export XDG_DATA_DIRS=$GSETTINGS_SCHEMAS_PATH:$XDG_DATA_DIRS
    export WEBVIEW_LIB_DIR=${webview-lib}/lib
    # Add clan-cli to the python path so that we can import it without building it in nix first
    export PYTHONPATH="$(pwd)":"$PYTHONPATH"
    popd

    ## Webview UI
    # Add clan-app-ui scripts to PATH
    pushd "$CLAN_CORE_PATH/pkgs/clan-app/ui"
    export NODE_PATH="$(pwd)/node_modules"
    export PATH="$NODE_PATH/.bin:$(pwd)/bin:$PATH"
    cp -r ${self'.packages.fonts} .fonts
    chmod -R +w .fonts
    mkdir -p api
    cp -r ${clan-ts-api}/* api
    chmod -R +w api
    popd

    # configure process-compose
    if test -f "$GIT_ROOT/pkgs/clan-app/.local.env"; then
      source "$GIT_ROOT/pkgs/clan-app/.local.env"
    fi
    export PC_CONFIG_FILES="$CLAN_CORE_PATH/pkgs/clan-app/process-compose.yaml"

    echo -e "${GREEN}To launch a qemu VM for testing, run:\n  start-vm <number of VMs>${NC}"
  '';
}
