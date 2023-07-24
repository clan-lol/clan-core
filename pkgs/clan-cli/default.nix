{ pkgs ? import <nixpkgs> { }
, lib ? pkgs.lib
, python3 ? pkgs.python3
, ruff ? pkgs.ruff
, runCommand ? pkgs.runCommand
, installShellFiles ? pkgs.installShellFiles
,
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
    passthru.tests = { inherit clan-tests clan-mypy; };
    passthru.devDependencies = devDependencies;
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

  clan-tests = runCommand "${name}-tests" { } ''
    cp -r ${src} ./src
    chmod +w -R ./src
    cd src
    ${checkPython}/bin/python -m pytest ./tests \
      || echo -e "generate coverage report py running:\n  pytest; firefox .reports/html/index.html"
    touch $out
  '';

in
package
