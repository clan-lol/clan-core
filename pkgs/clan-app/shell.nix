{
  lib,
  stdenv,
  clan-app,
  mkShell,
  ruff,
  desktop-file-utils,
  xdg-utils,
  mypy,
  python3,
  gtk4,
  libadwaita,
  webview-ui,
  self',
}:

let
  devshellTestDeps =
    clan-app.externalTestDeps
    ++ (with python3.pkgs; [
      rope
      mypy
      ipdb
      setuptools
      wheel
      pip
    ]);
in
mkShell {
  inherit (clan-app) nativeBuildInputs;

  inputsFrom = [ self'.devShells.default ];

  buildInputs =
    [
      ruff
      gtk4.dev # has the demo called 'gtk4-widget-factory'
      libadwaita.devdoc # has the demo called 'adwaita-1-demo'
    ]
    ++ devshellTestDeps

    # Dependencies for testing for linux hosts
    ++ (lib.optionals stdenv.isLinux [
      xdg-utils # install desktop files
      desktop-file-utils # verify desktop files
    ]);

  PYTHONBREAKPOINT = "ipdb.set_trace";

  shellHook = ''
    export GIT_ROOT=$(git rev-parse --show-toplevel)
    export PKG_ROOT=$GIT_ROOT/pkgs/clan-app

    # Add clan-app command to PATH
    export PATH="$PKG_ROOT/bin":"$PATH"

    # Add clan-cli to the python path so that we can import it without building it in nix first
    export PYTHONPATH="$GIT_ROOT/pkgs/clan-cli":"$PYTHONPATH"

    # Add the webview-ui to the .webui directory
    rm -rf ./clan_app/.webui/*
    mkdir -p ./clan_app/.webui
    cp -a ${webview-ui}/lib/node_modules/@clan/webview-ui/dist/* ./clan_app/.webui
    chmod -R +w ./clan_app/.webui
  '';
}
