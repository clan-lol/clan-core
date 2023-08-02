{ pkgs
, lib
, python3
, ruff
, runCommand
, installShellFiles
, zerotierone
, bubblewrap
, sops
, age
, self
}:
let
  pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  name = pyproject.project.name;

  src = lib.cleanSource ./.;

  dependencies = lib.attrValues {
    inherit (python3.pkgs)
      argcomplete
      ;
  };

  devDependencies = lib.attrValues {
    inherit (pkgs) ruff;
    inherit (python3.pkgs)
      black
      mypy
      pytest
      pytest-cov
      pytest-subprocess
      setuptools
      wheel
      ;
  };

  package = python3.pkgs.buildPythonPackage {
    inherit name src;
    format = "pyproject";
    nativeBuildInputs = [
      python3.pkgs.setuptools
      installShellFiles
    ];
    propagatedBuildInputs =
      dependencies
      ++ [ ];
    passthru.tests = { inherit clan-mypy clan-pytest; };
    passthru.devDependencies = devDependencies;

    makeWrapperArgs = [
      "--set CLAN_FLAKE ${self}"
    ];

    postInstall = ''
      installShellCompletion --bash --name clan \
        <(${python3.pkgs.argcomplete}/bin/register-python-argcomplete --shell bash clan)
      installShellCompletion --fish --name clan.fish \
        <(${python3.pkgs.argcomplete}/bin/register-python-argcomplete --shell fish clan)
    '';
    meta.mainProgram = "clan";
  };

  checkPython = python3.withPackages (_ps: devDependencies ++ dependencies);

  clan-mypy = runCommand "${name}-mypy" { } ''
    cp -r ${src} ./src
    chmod +w -R ./src
    cd src
    ${checkPython}/bin/mypy .
    touch $out
  '';

  clan-pytest = runCommand "${name}-tests"
    {
      nativeBuildInputs = [ zerotierone bubblewrap sops age ];
    } ''
    cp -r ${src} ./src
    chmod +w -R ./src
    cd src
    ${checkPython}/bin/python -m pytest ./tests
    touch $out
  '';
in
package
