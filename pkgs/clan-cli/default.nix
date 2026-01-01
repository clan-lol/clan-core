{
  # callPackage args
  gnupg,
  passage,
  installShellFiles,
  pass,
  jq,
  lib,
  nix,
  pkgs,
  runCommand,
  stdenv,
  # custom args
  clan-core-path,
  includedRuntimeDeps,
  nix-select,
  nixpkgs,
  pythonRuntime,
  setupNixInNix,
  templateDerivation,
  zerotierone,
  minifakeroot,
  nixosConfigurations,
  ...
}@args:
let
  pyDeps = ps: [
    ps.argcomplete # Enables shell completions

    # uncomment web-pdb for debugging:
    # (pkgs.callPackage ./python-deps.nix { }).web-pdb
  ];
  devDeps = ps: [
    ps.ipython
  ];
  pyTestDeps =
    ps:
    [
      ps.pytest
      ps.pytest-subprocess
      ps.pytest-xdist
      ps.pytest-timeout
      ps.pytest-cov
    ]
    ++ (pyDeps ps);
  pythonRuntimeWithDeps = pythonRuntime.withPackages (ps: pyDeps ps);

  # load nixpkgs runtime dependencies from a json file
  # This file represents an allow list at the same time that is checked by the run_cmd
  #   implementation in nix.py
  allDependencies = lib.importJSON ./clan_lib/nix/allowed-packages.json;
  # Use function args first to respect overlays and explicit overrides (e.g., nix -> lix)
  generateRuntimeDependenciesMap =
    deps:
    lib.filterAttrs (_: pkg: !(pkg.meta.unsupported or false)) (
      lib.genAttrs deps (name: args.${name} or pkgs.${name})
    );
  testRuntimeDependenciesMap = generateRuntimeDependenciesMap allDependencies;
  # Filter out packages that are not needed for tests and pull in many dependencies
  testExcludedPackages = {
    virt-viewer = true; # pulls in libvirt and other graphics libraries
    waypipe = true; # wayland forwarding not needed in tests
    zenity = true; # GUI dialogs not needed in tests
  };
  testRuntimeDependencies = lib.filter (pkg: !(testExcludedPackages.${pkg.pname or ""} or false)) (
    lib.attrValues testRuntimeDependenciesMap
  );
  bundledRuntimeDependenciesMap = generateRuntimeDependenciesMap includedRuntimeDeps;
  bundledRuntimeDependencies = lib.attrValues bundledRuntimeDependenciesMap;

  testDependencies = testRuntimeDependencies ++ [
    gnupg
    pass
    passage
    stdenv.cc # Compiler used for certain native extensions
    (pythonRuntime.withPackages pyTestDeps)
  ];

  nixFilter = import ../../lib/filter-clan-core/nix-filter.nix;

  cliSource =
    source:
    runCommand "clan-cli-source"
      {
        nativeBuildInputs = [ jq ];
      }
      ''
        cp -r ${source} $out
        chmod -R +w $out

        # In cases where the devshell created this file, this will already exist
        rm -f $out/clan_lib/nixpkgs
        rm -f $out/clan_lib/select

        substituteInPlace $out/clan_lib/flake/flake.py \
          --replace-fail '@select_hash@' "$(jq -r '.nodes."nix-select".locked.narHash' ${../../flake.lock})"
        ln -sf ${nixpkgs'} $out/clan_lib/nixpkgs
        ln -sf ${nix-select} $out/clan_lib/select
        cp -r ${../../templates} $out/clan_lib/clan_core_templates
      '';

  sourceWithoutTests = cliSource (
    nixFilter.filter {
      root = ./.;
      exclude = [
        # exclude if
        (
          _root: path: _type:
          (builtins.match ".*/test_[^/]+\.py" path) != null # matches test_*.py
          && (builtins.match ".*/[^/]+_test\.py" path) != null # matches *_test.py
        )
      ];
    }
  );
  sourceWithTests = cliSource ./.;

  # Create a custom nixpkgs for use within the project
  nixpkgs' =
    runCommand "nixpkgs"
      {
        # Not all versions have `nix flake update --flake` option
        nativeBuildInputs = [ nix ];
      }
      ''
        mkdir $out
        cat > $out/flake.nix << EOF
        {
          description = "dependencies for the clan-cli";

          inputs = {
            nixpkgs.url = "path://${nixpkgs}";
          };

          outputs = _inputs: { };
        }
        EOF
        ln -sf ${nixpkgs} $out/path
        HOME=$TMPDIR nix flake update --flake $out \
          --store ./. \
          --extra-experimental-features 'nix-command flakes'
      '';
in
pythonRuntime.pkgs.buildPythonApplication {
  name = "clan-cli";
  src = sourceWithoutTests;
  format = "pyproject";

  # Arguments for the wrapper to unset LD_LIBRARY_PATH to avoid glibc version issues
  makeWrapperArgs = [
    "--unset LD_LIBRARY_PATH"
    "--unset PYTHONPATH"

    # include selected runtime dependencies in the PATH
    "--prefix"
    "PATH"
    ":"
    (lib.makeBinPath (lib.attrValues bundledRuntimeDependenciesMap))

    "--set"
    "CLAN_PROVIDED_PACKAGES"
    (lib.concatStringsSep ":" (lib.attrNames bundledRuntimeDependenciesMap))
  ];

  nativeBuildInputs = [
    (pythonRuntime.withPackages (ps: [ ps.setuptools ]))
    installShellFiles
  ];

  propagatedBuildInputs = [ pythonRuntimeWithDeps ] ++ bundledRuntimeDependencies;

  passthru.tests = {
    clan-deps = pkgs.runCommand "clan-deps" { } ''
      # ${builtins.toString (builtins.attrValues testRuntimeDependenciesMap)}
      touch $out
    '';
    clan-pytest-without-core =
      runCommand "clan-pytest-without-core"
        {
          nativeBuildInputs = testDependencies;
          closureInfo = pkgs.closureInfo {
            rootPaths = [
              templateDerivation
            ];
          };
        }
        ''
          set -euo pipefail
          cp -r ${sourceWithTests} ./src
          chmod +w -R ./src
          cd ./src

          export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1 PYTHONWARNINGS=error

          # required to prevent concurrent 'nix flake lock' operations
          export CLAN_TEST_STORE=$TMPDIR/store
          export LOCK_NIX=$TMPDIR/nix_lock
          mkdir -p "$CLAN_TEST_STORE/nix/store"

          # limit build cores to 16
          jobs="$((NIX_BUILD_CORES>16 ? 16 : NIX_BUILD_CORES))"

          python -m pytest -m "not service_runner and not impure and not with_core" -n "$jobs" \
            ./clan_cli  \
            ./clan_lib  \
            --cov ./clan_cli \
            --cov ./clan_lib \
            --cov-report=html --cov-report=term

          mkdir -p $out
          cp -r . $out
        '';
  }
  // lib.optionalAttrs (!stdenv.isDarwin) {
    # disabled on macOS until we fix all remaining issues
    clan-pytest-with-core =
      runCommand "clan-pytest-with-core"
        {
          nativeBuildInputs = testDependencies;
          buildInputs = [
            pkgs.bash
            pkgs.coreutils
            nix
          ];
          closureInfo = pkgs.closureInfo {
            rootPaths = [
              templateDerivation
              pkgs.bash
              pkgs.coreutils
              pkgs.jq.dev
              pkgs.stdenv
              pkgs.stdenvNoCC
              pkgs.openssh
              pkgs.shellcheck-minimal
              pkgs.mkpasswd
              pkgs.xkcdpass
              pkgs.pass
              pkgs.passage
              zerotierone
              # needed by vars generate tests
              (pkgs.callPackage ../../pkgs/zerotierone { includeController = true; })
              minifakeroot
              nix-select
              ../../nixosModules/clanCore/zerotier/generate.py

              # needed by flash list tests
              pkgs.kbd.out
              pkgs.glibcLocales

              # Pre-built VMs for impure tests
              pkgs.stdenv.drvPath
              pkgs.bash.drvPath
              pkgs.buildPackages.xorg.lndir
              (pkgs.perl.withPackages (
                p: with p; [
                  ConfigIniFiles
                  FileSlurp
                ]
              ))
              (pkgs.closureInfo { rootPaths = [ ]; }).drvPath
              pkgs.desktop-file-utils
              pkgs.dbus
              pkgs.unzip
              pkgs.libxslt
              pkgs.getconf
              # REMOVEME: once we drop support for 25.11
              (if pkgs ? chroot-realpath then pkgs.chroot-realpath else pkgs.nixos-init)

              nixosConfigurations."test-vm-persistence-${stdenv.hostPlatform.system}".config.system.build.toplevel
              nixosConfigurations."test-vm-deployment-${stdenv.hostPlatform.system}".config.system.build.toplevel

              nixosConfigurations."test-vm-persistence-${stdenv.hostPlatform.system}".config.system.clan.vm.create
              nixosConfigurations."test-vm-deployment-${stdenv.hostPlatform.system}".config.system.clan.vm.create
            ];
          };
        }
        ''
          set -euo pipefail
          cp -r ${sourceWithTests} ./src
          chmod +w -R ./src
          cd ./src

          ${setupNixInNix}

          export CLAN_CORE_PATH=${clan-core-path}
          export PYTHONWARNINGS=error

          # used for tests without flakes
          export NIXPKGS=${nixpkgs}
          export NIX_SELECT=${nix-select}

          # limit build cores to 16
          jobs="$((NIX_BUILD_CORES>16 ? 16 : NIX_BUILD_CORES))"

          # Run all tests with core marker
          python -m pytest -m "not service_runner and not impure and with_core" -n "$jobs" \
            ./clan_cli  \
            ./clan_lib  \
            --cov ./clan_cli \
            --cov ./clan_lib \
            --cov-report=html --cov-report=term

          mkdir -p $out
          cp -r . $out
        '';
  };

  passthru.nixpkgs = nixpkgs';
  passthru.devshellPyDeps = ps: (pyTestDeps ps) ++ (pyDeps ps) ++ (devDeps ps);
  passthru.pythonRuntime = pythonRuntime;
  passthru.runtimeDependencies = bundledRuntimeDependencies;
  passthru.runtimeDependenciesMap = bundledRuntimeDependenciesMap;
  passthru.testRuntimeDependencies = testRuntimeDependencies;
  passthru.testRuntimeDependenciesMap = testRuntimeDependenciesMap;
  passthru.sourceWithTests = sourceWithTests;

  # Nixpkgs doesn't get copied from `src` as it's not in `package-data` in `pyproject.toml`
  # as it significantly slows down the build so we copy it again here
  # We don't copy `select` using `package-data` as Python globs don't include hidden directories
  # leading to a different NAR hash and copying it here would also lead to `patchShebangs`
  # changing the contents
  postInstall = ''
    cp -arf clan_lib/clan_core_templates/* $out/${pythonRuntime.sitePackages}/clan_lib/clan_core_templates

    cp -r ${nixpkgs'} $out/${pythonRuntime.sitePackages}/clan_lib/nixpkgs
    ln -sf ${nix-select} $out/${pythonRuntime.sitePackages}/clan_lib/select
    installShellCompletion --bash --name clan \
      <(${pythonRuntimeWithDeps.pkgs.argcomplete}/bin/register-python-argcomplete --shell bash clan)
    installShellCompletion --fish --name clan.fish \
      <(${pythonRuntimeWithDeps.pkgs.argcomplete}/bin/register-python-argcomplete --shell fish clan)
    installShellCompletion --zsh --name _clan \
      <(${pythonRuntimeWithDeps.pkgs.argcomplete}/bin/register-python-argcomplete --shell zsh clan)
  '';

  # Clean up after the package to avoid leaking python packages into a devshell
  # TODO: factor separate cli / API packages
  postFixup = ''
    rm $out/nix-support/propagated-build-inputs
  '';

  checkPhase = ''
    $out/bin/clan --help
  '';

  meta.mainProgram = "clan";
}
