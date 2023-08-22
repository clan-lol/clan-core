{ age
, argcomplete
, black
, bubblewrap
, installShellFiles
, mypy
, nix
, openssh
, pytest
, pytest-cov
, pytest-subprocess
, python3
, ruff
, runCommand
, self
, setuptools
, sops
, stdenv
, wheel
, zerotierone
, rsync
}:
let
  # This provides dummy options for testing clan config and prevents it from
  # evaluating the flake .#
  CLAN_OPTIONS_FILE = ./clan_cli/config/jsonschema/options.json;

  dependencies = [ argcomplete ];

  testDependencies = [
    pytest
    pytest-cov
    pytest-subprocess
    mypy
    openssh
    stdenv.cc
  ];

  checkPython = python3.withPackages (_ps: dependencies ++ testDependencies);

  # - vendor the jsonschema nix lib (copy instead of symlink).
  # - lib.cleanSource prevents unnecessary rebuilds when `self` changes.
  source = runCommand "clan-cli-source" { } ''
    cp -r ${./.} $out
    chmod -R +w $out
    rm $out/clan_cli/config/jsonschema
    cp -r ${self + /lib/jsonschema} $out/clan_cli/config/jsonschema
  '';
in
python3.pkgs.buildPythonPackage {
  name = "clan-cli";
  src = source;
  format = "pyproject";

  inherit CLAN_OPTIONS_FILE;

  nativeBuildInputs = [
    setuptools
    installShellFiles
  ];
  propagatedBuildInputs = dependencies;

  passthru.tests = {
    clan-mypy = runCommand "clan-mypy" { } ''
      export CLAN_OPTIONS_FILE="${CLAN_OPTIONS_FILE}"
      cp -r ${source} ./src
      chmod +w -R ./src
      cd ./src
      ${checkPython}/bin/mypy .
      touch $out
    '';
    clan-pytest = runCommand "clan-tests"
      {
        nativeBuildInputs = [ age zerotierone bubblewrap sops nix openssh rsync stdenv.cc ];
      } ''
      export CLAN_OPTIONS_FILE="${CLAN_OPTIONS_FILE}"
      cp -r ${source} ./src
      chmod +w -R ./src
      cd ./src
      NIX_STATE_DIR=$TMPDIR/nix ${checkPython}/bin/python -m pytest -s ./tests
      touch $out
    '';
  };

  passthru.devDependencies = [
    ruff
    black
    setuptools
    wheel
  ] ++ testDependencies;

  makeWrapperArgs = [
    "--set CLAN_FLAKE ${self}"
  ];

  postInstall = ''
    installShellCompletion --bash --name clan \
      <(${argcomplete}/bin/register-python-argcomplete --shell bash clan)
    installShellCompletion --fish --name clan.fish \
      <(${argcomplete}/bin/register-python-argcomplete --shell fish clan)
  '';
  checkPhase = ''
    PYTHONPATH= $out/bin/clan --help
    if grep --include \*.py -Rq "breakpoint()" $out; then
      echo "breakpoint() found in $out:"
      grep --include \*.py -Rn "breakpoint()" $out
      exit 1
    fi
  '';
  meta.mainProgram = "clan";
}
