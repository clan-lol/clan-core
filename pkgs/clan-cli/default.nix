{ age
, lib
, argcomplete
, fastapi
, uvicorn
, installShellFiles
, nix
, openssh
, pytest
, pytest-cov
, pytest-xdist
, pytest-subprocess
, pytest-timeout
, remote-pdb
, ipdb
, python3
, runCommand
, setuptools
, sops
, stdenv
, wheel
, fakeroot
, rsync
, ui-assets
, bash
, sshpass
, zbar
, tor
, git
, nixpkgs
, makeDesktopItem
, copyDesktopItems
, qemu
, gnupg
, e2fsprogs
, mypy
, deal
, rope
, clan-core-path
, schemathesis
}:
let

  dependencies = [
    argcomplete # optional dependency: if not enabled, shell completion will not work
  ];

  pytestDependencies = runtimeDependencies ++ dependencies ++ [
    fastapi # optional dependencies: if not enabled, webui subcommand will not work
    uvicorn # optional dependencies: if not enabled, webui subcommand will not work

    #schemathesis # optional for http fuzzing
    pytest
    pytest-cov
    pytest-subprocess
    pytest-xdist
    pytest-timeout
    deal
    remote-pdb
    ipdb
    openssh
    git
    gnupg
    stdenv.cc
  ];

  # Optional dependencies for clan cli, we re-expose them here to make sure they all build.
  runtimeDependencies = [
    bash
    nix
    fakeroot
    openssh
    sshpass
    zbar
    tor
    age
    rsync
    sops
    git
    mypy
    qemu
    e2fsprogs
  ];

  runtimeDependenciesAsSet = builtins.listToAttrs (builtins.map (p: lib.nameValuePair (lib.getName p.name) p) runtimeDependencies);

  checkPython = python3.withPackages (_ps: pytestDependencies);

  # - vendor the jsonschema nix lib (copy instead of symlink).
  # Interesting fact: using nixpkgs from flakes instead of nixpkgs.path is reduces evaluation time by 5s.
  source = runCommand "clan-cli-source" { } ''
    cp -r ${./.} $out
    chmod -R +w $out
    rm $out/clan_cli/config/jsonschema
    ln -s ${nixpkgs'} $out/clan_cli/nixpkgs
    cp -r ${../../lib/jsonschema} $out/clan_cli/config/jsonschema
    ln -s ${ui-assets} $out/clan_cli/webui/assets
  '';
  nixpkgs' = runCommand "nixpkgs" { nativeBuildInputs = [ nix ]; } ''
    mkdir $out
    cat > $out/flake.nix << EOF
    {
      description = "dependencies for the clan-cli";

      inputs = {
        nixpkgs.url = "nixpkgs";
      };

      outputs = _inputs: { };
    }
    EOF
    ln -s ${nixpkgs} $out/path
    nix flake lock $out \
      --store ./. \
      --extra-experimental-features 'nix-command flakes' \
      --override-input nixpkgs ${nixpkgs}
  '';
in
python3.pkgs.buildPythonApplication {
  name = "clan-cli";
  src = source;
  format = "pyproject";

  makeWrapperArgs = [
    # This prevents problems with mixed glibc versions that might occur when the
    # cli is called through a browser built against another glibc
    "--unset LD_LIBRARY_PATH"
  ];

  nativeBuildInputs = [
    setuptools
    installShellFiles
    copyDesktopItems
  ];
  propagatedBuildInputs = dependencies;

  # also re-expose dependencies so we test them in CI
  passthru.tests = (lib.mapAttrs' (n: lib.nameValuePair "clan-dep-${n}") runtimeDependenciesAsSet) // rec {
    clan-pytest-without-core = runCommand "clan-pytest-without-core" { nativeBuildInputs = [ checkPython ] ++ pytestDependencies; } ''
      cp -r ${source} ./src
      chmod +w -R ./src
      cd ./src

      export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1
      ${checkPython}/bin/python -m pytest -m "not impure and not with_core" -s ./tests
      touch $out
    '';
    # separate the tests that can never be cached
    clan-pytest-with-core = runCommand "clan-pytest-with-core" { nativeBuildInputs = [ checkPython ] ++ pytestDependencies; } ''
      cp -r ${source} ./src
      chmod +w -R ./src
      cd ./src

      export CLAN_CORE=${clan-core-path}
      export NIX_STATE_DIR=$TMPDIR/nix IN_NIX_SANDBOX=1
      ${checkPython}/bin/python -m pytest -m "not impure and with_core" -s ./tests
      touch $out
    '';
    clan-pytest = runCommand "clan-pytest" { } ''
      echo ${clan-pytest-without-core}
      echo ${clan-pytest-with-core}
      touch $out
    '';
    check-for-breakpoints = runCommand "breakpoints" { } ''
      if grep --include \*.py -Rq "breakpoint()" ${source}; then
        echo "breakpoint() found in ${source}:"
        grep --include \*.py -Rn "breakpoint()" ${source}
        exit 1
      fi
      touch $out
    '';
  };
  passthru.clan-openapi = runCommand "clan-openapi" { } ''
    cp -r ${source} ./src
    chmod +w -R ./src
    cd ./src
    export PATH=${checkPython}/bin:$PATH

    ${checkPython}/bin/python ./bin/gen-openapi --out $out/openapi.json --app-dir . clan_cli.webui.app:app
    touch $out
  '';
  passthru.nixpkgs = nixpkgs';
  passthru.checkPython = checkPython;

  passthru.devDependencies = [
    rope
    setuptools
    wheel
  ] ++ pytestDependencies;

  passthru.pytestDependencies = pytestDependencies;
  passthru.runtimeDependencies = runtimeDependencies;

  postInstall = ''
    cp -r ${nixpkgs'} $out/${python3.sitePackages}/clan_cli/nixpkgs
    installShellCompletion --bash --name clan \
      <(${argcomplete}/bin/register-python-argcomplete --shell bash clan)
    installShellCompletion --fish --name clan.fish \
      <(${argcomplete}/bin/register-python-argcomplete --shell fish clan)
  '';
  # Don't leak python packages into a devshell.
  # It can be very confusing if you `nix run` than load the cli from the devshell instead.
  postFixup = ''
    rm $out/nix-support/propagated-build-inputs
  '';
  checkPhase = ''
    PYTHONPATH= $out/bin/clan --help
  '';
  meta.mainProgram = "clan";
  desktopItems = [
    (makeDesktopItem {
      name = "clan";
      exec = "clan --debug join %u";
      desktopName = "CLan Manager";
      startupWMClass = "clan";
      mimeTypes = [ "x-scheme-handler/clan" ];
    })
  ];
}
