{ python3
, runCommand
, setuptools
, copyDesktopItems
, pygobject3
, wrapGAppsHook
, gtk4
, gnome
, gobject-introspection
, clan-cli
, makeDesktopItem
, libadwaita
}:
let
  source = ./.;
in
python3.pkgs.buildPythonApplication {
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

  buildInputs = [ gtk4 libadwaita gnome.adwaita-icon-theme ];
  propagatedBuildInputs = [ pygobject3 clan-cli ];

  # also re-expose dependencies so we test them in CI
  passthru.tests = {
    clan-vm-manager-no-breakpoints = runCommand "clan-vm-manager-no-breakpoints" { } ''
      if grep --include \*.py -Rq "breakpoint()" ${source}; then
        echo "breakpoint() found in ${source}:"
        grep --include \*.py -Rn "breakpoint()" ${source}
        exit 1
      fi
      touch $out
    '';
  };

  # Don't leak python packages into a devshell.
  # It can be very confusing if you `nix run` than load the cli from the devshell instead.
  postFixup = ''
    rm $out/nix-support/propagated-build-inputs
  '';
  checkPhase = ''
    PYTHONPATH= $out/bin/clan-vm-manager --help
  '';
  desktopItems = [
    (makeDesktopItem {
      name = "lol.clan.vm.manager";
      exec = "clan-vm-manager %u";
      icon = ./clan_vm_manager/assets/clan_white.png;
      desktopName = "cLAN Manager";
      startupWMClass = "clan";
      mimeTypes = [ "x-scheme-handler/clan" ];
    })
  ];
}
