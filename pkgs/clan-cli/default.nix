{ lib
, python3
, ruff
, runCommand
, installShellFiles
, zerotierone
, bubblewrap
, sops
, age
, black
, nix
, mypy
, setuptools
, self
, argcomplete
, pytest
, pytest-cov
, pytest-subprocess
, wheel
}:
let
  dependencies = [ argcomplete ];

  testDependencies = [
    pytest
    pytest-cov
    pytest-subprocess
    mypy
  ];

  checkPython = python3.withPackages (_ps: dependencies ++ testDependencies);
in
python3.pkgs.buildPythonPackage {
  name = "clan-cli";
  src = lib.cleanSource ./.;
  format = "pyproject";
  nativeBuildInputs = [
    setuptools
    installShellFiles
  ];
  propagatedBuildInputs = dependencies;

  preBuild = ''
    rm ./clan_cli/config/jsonschema
    cp -r ${self}/lib/jsonschema ./clan_cli/config/jsonschema
  '';

  passthru.tests = {
    clan-mypy = runCommand "clan-mypy" { } ''
      cp -r ${self} ./flake
      chmod +w -R ./flake
      cd ./flake/pkgs/clan-cli
      ${checkPython}/bin/mypy .
      touch $out
    '';
    clan-pytest = runCommand "clan-tests"
      {
        nativeBuildInputs = [ age zerotierone bubblewrap sops nix ];
      } ''
      cp -r ${self} ./flake
      chmod +w -R ./flake
      cd ./flake/pkgs/clan-cli
      ${checkPython}/bin/python -m pytest ./tests
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
