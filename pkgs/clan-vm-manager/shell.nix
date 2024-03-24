{
  lib,
  stdenv,
  clan-vm-manager,
  mkShell,
  ruff,
  desktop-file-utils,
  xdg-utils,
  mypy,
  python3,
  gtk4,
  libadwaita,
}:

let
  devshellTestDeps =
    clan-vm-manager.testDependencies
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
  inherit (clan-vm-manager) nativeBuildInputs;
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

  shellHook = ''
    export PATH=$(pwd)/bin:$PATH
  '';
}
