{
  runCommand,
  copyDesktopItems,
  clan-cli,
  makeDesktopItem,
  clan-app-ui,
  webview-lib,
  fontconfig,
  pythonRuntime,
  wrapGAppsHook4,
  gobject-introspection,
  gtk4,
  lib,
  stdenv,
  # macOS-specific dependencies
  imagemagick,
  makeWrapper,
  libicns,
  nodejs_24,
}:
let
  source =
    {
      withTests ? true,
    }:
    lib.fileset.toSource {
      root = ./.;
      fileset = lib.fileset.unions (
        [
          ./clan_app
          ./pyproject.toml
        ]
        ++ lib.optional withTests ./tests
      );
    };

  desktop-file = makeDesktopItem {
    name = "org.clan.app";
    exec = "clan-app %u";
    icon = "clan-app";
    desktopName = "Clan App";
    startupWMClass = "clan";
    mimeTypes = [ "x-scheme-handler/clan" ];
  };

  runtimeDependencies = [
    gobject-introspection
    gtk4
    nodejs_24
  ];

  pyDeps = ps: [
    ps.pygobject3
    ps.pygobject-stubs
  ];

  # Dependencies required for running tests
  pyTestDeps =
    ps:
    [
      # Testing framework
      ps.pytest
      ps.pytest-subprocess # fake the real subprocess behavior to make your tests more independent.
      ps.pytest-xdist # Run tests in parallel on multiple cores
      ps.pytest-timeout # Add timeouts to your tests
    ]
    ++ ps.pytest.propagatedBuildInputs;

  clan-cli-module = [
    (pythonRuntime.pkgs.toPythonModule (clan-cli.override { inherit pythonRuntime; }))
  ];

in
pythonRuntime.pkgs.buildPythonApplication {
  name = "clan-app";
  src = source { };
  format = "pyproject";

  dontWrapGApps = true;
  preFixup = ''
    makeWrapperArgs+=(
      --set FONTCONFIG_FILE ${fontconfig.out}/etc/fonts/fonts.conf
      --set WEBUI_PATH "$out/${pythonRuntime.sitePackages}/clan_app/.webui"
      --set WEBVIEW_LIB_DIR "${webview-lib}/lib"
      # This prevents problems with mixed glibc versions that might occur when the
      # cli is called through a browser built against another glibc
      --unset LD_LIBRARY_PATH
      "''${gappsWrapperArgs[@]}"
    )
  '';

  # Deps needed only at build time
  nativeBuildInputs = [
    (pythonRuntime.withPackages (ps: [ ps.setuptools ]))
    copyDesktopItems
    fontconfig

    # gtk4 deps
    wrapGAppsHook4
  ]
  ++ runtimeDependencies
  ++ lib.optionals stdenv.hostPlatform.isDarwin [
    imagemagick
    makeWrapper
    libicns
  ];

  # The necessity of setting buildInputs and propagatedBuildInputs to the
  # same values for your Python package within Nix largely stems from ensuring
  # that all necessary dependencies are consistently available both
  # at build time and runtime,
  propagatedBuildInputs = [
    (pythonRuntime.withPackages (ps: clan-cli-module ++ (pyDeps ps)))
  ]
  ++ runtimeDependencies;

  # also re-expose dependencies so we test them in CI
  passthru = {
    tests = {
      clan-app-pytest =
        runCommand "clan-app-pytest"
          {
            buildInputs = runtimeDependencies ++ [
              (pythonRuntime.withPackages (ps: clan-cli-module ++ (pyTestDeps ps) ++ (pyDeps ps)))
              fontconfig
            ];
          }
          ''
            cp -r ${source { withTests = true; }} ./src
            chmod +w -R ./src
            cd ./src

            export FONTCONFIG_FILE=${fontconfig.out}/etc/fonts/fonts.conf
            export FONTCONFIG_PATH=${fontconfig.out}/etc/fonts

            mkdir -p .home/.local/share/fonts
            export HOME=.home

            fc-cache --verbose
            # > fc-cache succeeded

            echo "Loaded the following fonts ..."
            fc-list

            echo "STARTING ..."
            export WEBVIEW_LIB_DIR="${webview-lib}/lib"
            export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1
            export PYTHONPATH="$PWD:$PYTHONPATH"
            pytest -s -m "not impure" ./tests
            touch $out
          '';
    };
  };

  # Additional pass-through attributes
  passthru.desktop-file = desktop-file;
  passthru.devshellPyDeps = ps: (pyTestDeps ps) ++ (pyDeps ps);
  passthru.runtimeDeps = runtimeDependencies;
  passthru.pythonRuntime = pythonRuntime;

  postInstall = ''
    mkdir -p $out/${pythonRuntime.sitePackages}/clan_app/.webui
    cp -r ${clan-app-ui}/lib/node_modules/@clan/ui/dist/* $out/${pythonRuntime.sitePackages}/clan_app/.webui

    ${lib.optionalString (!stdenv.hostPlatform.isDarwin) ''
      mkdir -p $out/share/icons/hicolor
      cp -r ./clan_app/assets/white-favicons/* $out/share/icons/hicolor
    ''}

    ${lib.optionalString stdenv.hostPlatform.isDarwin ''
      set -eu pipefail
      # Create macOS app bundle structure
      mkdir -p "$out/Applications/Clan App.app/Contents/"{MacOS,Resources}

      # Create Info.plist
      cat > "$out/Applications/Clan App.app/Contents/Info.plist" << 'EOF'
      <?xml version="1.0" encoding="UTF-8"?>
      <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
      <plist version="1.0">
      <dict>
          <key>CFBundleDisplayName</key>
          <string>Clan App</string>
          <key>CFBundleExecutable</key>
          <string>Clan App</string>
          <key>CFBundleIconFile</key>
          <string>clan-app.icns</string>
          <key>CFBundleIdentifier</key>
          <string>org.clan.app</string>
          <key>CFBundleName</key>
          <string>Clan App</string>
          <key>CFBundlePackageType</key>
          <string>APPL</string>
          <key>CFBundleShortVersionString</key>
          <string>1.0</string>
          <key>CFBundleVersion</key>
          <string>1.0</string>
          <key>NSHighResolutionCapable</key>
          <true/>
          <key>NSPrincipalClass</key>
          <string>NSApplication</string>
          <key>CFBundleInfoDictionaryVersion</key>
          <string>6.0</string>
          <key>CFBundleURLTypes</key>
          <array>
              <dict>
                  <key>CFBundleURLName</key>
                  <string>Clan Protocol</string>
                  <key>CFBundleURLSchemes</key>
                  <array>
                      <string>clan</string>
                  </array>
              </dict>
          </array>
      </dict>
      </plist>
      EOF

      # Create app icon (convert PNG to ICNS using minimal approach to avoid duplicates)
      # Create a temporary iconset directory structure
      mkdir clan-app.iconset

      # Create a minimal iconset with only essential, non-duplicate sizes
      # Each PNG file should map to a unique ICNS type
      cp ./clan_app/assets/white-favicons/16x16/apps/clan-app.png clan-app.iconset/icon_16x16.png
      cp ./clan_app/assets/white-favicons/128x128/apps/clan-app.png clan-app.iconset/icon_128x128.png

      # Use libicns png2icns tool to create proper ICNS file with minimal set
      png2icns "$out/Applications/Clan App.app/Contents/Resources/clan-app.icns" \
        clan-app.iconset/icon_16x16.png \
        clan-app.iconset/icon_128x128.png

      # Create PkgInfo file (standard requirement for macOS apps)
      echo -n "APPL????" > "$out/Applications/Clan App.app/Contents/PkgInfo"

      # Create the main executable script with proper process name
      cat > "$out/Applications/Clan App.app/Contents/MacOS/Clan App" << EOF
      #!/bin/bash
      # Execute with the correct process name for app icon to appear
      exec -a "\$0" "$out/bin/.clan-app-orig" "\$@"
      EOF

      chmod +x "$out/Applications/Clan App.app/Contents/MacOS/Clan App"
      set +eu pipefail
    ''}
  '';

  # TODO: If we start clan-app over the cli the process name is "python" and icons don't show up correctly on macOS
  # I looked in how blender does it, but couldn't figure it out yet.
  # They do an exec -a in their wrapper script, but that doesn't seem to work here.

  # Don't leak python packages into a devshell.
  # It can be very confusing if you `nix run` than load the cli from the devshell instead.
  postFixup = ''
    rm $out/nix-support/propagated-build-inputs
  ''
  + lib.optionalString stdenv.hostPlatform.isDarwin ''
    set -eu pipefail
    mv $out/bin/clan-app $out/bin/.clan-app-orig


    # Create command line wrapper that executes the app bundle
    cat > $out/bin/clan-app << EOF
    #!/bin/bash
    exec "$out/Applications/Clan App.app/Contents/MacOS/Clan App" "\$@"
    EOF
    chmod +x $out/bin/clan-app
    set +eu pipefail
  '';
  checkPhase = ''
    set -eu pipefail
    export FONTCONFIG_FILE=${fontconfig.out}/etc/fonts/fonts.conf
    export FONTCONFIG_PATH=${fontconfig.out}/etc/fonts

    mkdir -p .home/.local/share/fonts
    export HOME=.home

    fc-cache --verbose
    # > fc-cache succeeded

    echo "Loaded the following fonts ..."
    fc-list

    PYTHONPATH= $out/bin/clan-app --help
    set +eu pipefail
  '';
  desktopItems = [ desktop-file ];
}
