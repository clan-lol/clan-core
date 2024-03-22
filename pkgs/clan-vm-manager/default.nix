{
  python3,
  runCommand,
  setuptools,
  copyDesktopItems,
  pygobject3,
  wrapGAppsHook,
  gtk4,
  gnome,
  pygobject-stubs,
  gobject-introspection,
  clan-cli,
  makeDesktopItem,
  libadwaita,
  weston,
}:
let
  source = ./.;
  desktop-file = makeDesktopItem {
    name = "org.clan.vm-manager";
    exec = "clan-vm-manager %u";
    icon = ./clan_vm_manager/assets/clan_white.png;
    desktopName = "cLAN Manager";
    startupWMClass = "clan";
    mimeTypes = [ "x-scheme-handler/clan" ];
  };
in
python3.pkgs.buildPythonApplication rec {
  name = "clan-vm-manager";
  src = source;
  format = "pyproject";

  makeWrapperArgs = [
    # This prevents problems with mixed glibc versions that might occur when the
    # cli is called through a browser built against another glibc
    "--unset LD_LIBRARY_PATH"
  ];

  nativeBuildInputs = [
    setuptools
    copyDesktopItems
    wrapGAppsHook
    gobject-introspection
  ];

  buildInputs = [
    gtk4
    libadwaita
    gnome.adwaita-icon-theme
  ];

  # We need to propagate the build inputs to nix fmt / treefmt
  propagatedBuildInputs = [
    (python3.pkgs.toPythonModule clan-cli)
    passthru.externalPythonDeps
  ];

  checkPython = python3.withPackages (_ps: clan-cli.passthru.pytestDependencies);

  devDependencies = [
    checkPython
    weston
  ] ++ nativeBuildInputs ++ buildInputs ++ propagatedBuildInputs;

  passthru.checkPython = checkPython;
  passthru.devDependencies = devDependencies;

  # also re-expose dependencies so we test them in CI
  passthru = {
    inherit desktop-file;
    # Keep external dependencies in a separate lists to refer to thm elsewhere
    # This helps avoiding issues like dev-shells accidentally depending on
    #   nix derivations of local packages.
    externalPythonDeps = [
      pygobject3
      pygobject-stubs
    ];
    tests = {
      clan-vm-manager-pytest =
        runCommand "clan-vm-manager-pytest" { nativeBuildInputs = devDependencies; }
          ''
            cp -r ${source} ./src
            chmod +w -R ./src
            cd ./src

            export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1
            ${checkPython}/bin/python -m pytest -m "not impure" ./tests
            touch $out
          '';
      clan-vm-manager-no-breakpoints = runCommand "clan-vm-manager-no-breakpoints" { } ''
        if grep --include \*.py -Rq "breakpoint()" ${source}; then
          echo "breakpoint() found in ${source}:"
          grep --include \*.py -Rn "breakpoint()" ${source}
          exit 1
        fi
        touch $out
      '';
    };
  };

  # Don't leak python packages into a devshell.
  # It can be very confusing if you `nix run` than load the cli from the devshell instead.
  postFixup = ''
    rm $out/nix-support/propagated-build-inputs
  '';
  checkPhase = ''
    PYTHONPATH= $out/bin/clan-vm-manager --help
  '';
  desktopItems = [ desktop-file ];
}
