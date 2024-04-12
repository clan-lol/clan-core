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
  tigervnc,
  libvncserver,
}:

let
  devshellTestDeps =
    clan-vm-manager.externalTestDeps
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
      tigervnc
      libvncserver.dev
      libvncserver
    ]
    ++ devshellTestDeps

    # Dependencies for testing for linux hosts
    ++ (lib.optionals stdenv.isLinux [
      xdg-utils # install desktop files
      desktop-file-utils # verify desktop files
    ]);

  # Use ipdb as the default debugger for python
  PYTHONBREAKPOINT = "ipdb.set_trace";

  hardeningDisabled = "all";

  shellHook = ''
    export LIBVNC_INCLUDE=${libvncserver.dev}/include
    export LIBVNC_LIB=${libvncserver}/lib

    export GIT_ROOT=$(git rev-parse --show-toplevel)

    # Add clan-vm-manager command to PATH
    export PATH="$GIT_ROOT/pkgs/clan-vm-manager/bin":"$PATH"

    # Add clan-vm-manager to the python path so that we can
    # import it in the tests
    export PYTHONPATH="$GIT_ROOT/pkgs/clan-vm-manager":"$PYTHONPATH"

    # Add clan-cli to the python path so that we can import it without building it in nix first
    export PYTHONPATH="$GIT_ROOT/pkgs/clan-cli":"$PYTHONPATH"

    # Add clan-cli to the PATH
    export PATH="$GIT_ROOT/pkgs/clan-cli/bin":"$PATH"
  '';
}
